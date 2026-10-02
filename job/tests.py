from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.db.migrations.executor import MigrationExecutor
from rest_framework.test import APIClient

from company.models import Company
from configs.models import ResumeConfig
from course.models import Batch, Course
from job.models import (
    Application,
    ApplicationAttributeValue,
    ApplicationStatus,
    Attribute,
    Job,
    JobAttribute,
    Resume,
    StudentAttributeValue,
    default_application_status_id,
)
from student.models import Student
from users.models import User, UserRole


class ApplicationStatusTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_directory = TemporaryDirectory()
        cls.media_settings = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_settings.disable()
        cls.media_directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.applied_status = ApplicationStatus.objects.get(code="applied")
        ResumeConfig.objects.create(
            max_resume_size=Decimal("20.00"),
            max_number_of_resumes=10,
        )

        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="password",
            role=UserRole.STUDENT,
        )
        course = Course.objects.create(name="Computer Science", semester=1, years=4)
        batch = Batch.objects.create(
            course=course,
            start_year=2025,
            end_year=2029,
        )
        self.student = Student.objects.create(user=self.student_user, batch=batch)

        self.company_user = User.objects.create_user(
            username="company",
            email="company@example.com",
            password="password",
            role=UserRole.COMPANY,
        )
        company = Company.objects.create(user=self.company_user, name="Example Company")
        self.job = Job.objects.create(
            company=company,
            batch=batch,
            title="Backend Engineer",
            description="Build APIs",
            location="Remote",
        )
        self.resume = Resume.objects.create(
            student=self.student,
            file=SimpleUploadedFile(
                "resume.pdf",
                b"%PDF-1.4 test resume",
                content_type="application/pdf",
            ),
        )

        self.client = APIClient()
        self.client.force_authenticate(self.student_user)

    def create_application(self, **kwargs):
        return Application.objects.create(
            student=self.student,
            job=self.job,
            **kwargs,
        )

    def test_application_model_defaults_to_applied_status(self):
        application = self.create_application()

        self.assertEqual(default_application_status_id(), self.applied_status.pk)
        self.assertEqual(application.status, self.applied_status)

    def test_status_endpoint_lists_and_creates_statuses(self):
        response = self.client.get("/job/application-statuses/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"id": self.applied_status.pk, "code": "applied", "name": "Applied"},
            response.data,
        )

        response = self.client.post(
            "/job/application-statuses/",
            {"name": "Interview"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Interview")
        self.assertEqual(response.data["code"], "interview")

        duplicate_response = self.client.post(
            "/job/application-statuses/",
            {"name": "Interview"},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)

    def test_status_endpoint_preserves_authenticated_only_permission(self):
        unauthenticated_client = APIClient()

        response = unauthenticated_client.get("/job/application-statuses/")

        self.assertIn(response.status_code, (401, 403))

    def test_application_create_uses_default_and_returns_applied(self):
        response = self.client.post(
            "/job/applications/",
            {"job": self.job.pk, "resume_id": self.resume.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], "Application submitted successfully")
        self.assertEqual(response.data["status"], "Applied")
        application = Application.objects.get(student=self.student, job=self.job)
        self.assertEqual(application.status, self.applied_status)

    def test_null_status_is_presented_as_applied_in_application_and_job_apis(self):
        application = self.create_application(status=None)

        detail_response = self.client.get(f"/job/applications/{application.pk}/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data["data"]["status"], "Applied")

        list_response = self.client.get("/job/applications/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data["data"][0]["status"], "Applied")

        jobs_response = self.client.get("/job/jobs/")
        self.assertEqual(jobs_response.status_code, 200)
        self.assertEqual(jobs_response.data["data"][0]["status"], "Applied")

        company_client = APIClient()
        company_client.force_authenticate(self.company_user)
        admin_list_response = company_client.get("/job/applications/")
        self.assertEqual(admin_list_response.status_code, 200)
        self.assertEqual(admin_list_response.data["data"][0]["status"], "Applied")

    def test_job_api_keeps_not_applied_for_a_job_without_an_application(self):
        response = self.client.get("/job/jobs/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["status"], "Not Applied")

    def test_application_status_can_be_assigned_by_id_or_existing_name(self):
        application = self.create_application()
        screening = ApplicationStatus.objects.create(name="Screening")

        response = self.client.patch(
            f"/job/applications/{application.pk}/",
            {"status": screening.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "Screening")

        response = self.client.patch(
            f"/job/applications/{application.pk}/",
            {"status": "Rejected"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "Rejected")

    def test_invalid_application_status_id_does_not_change_status(self):
        application = self.create_application()

        response = self.client.patch(
            f"/job/applications/{application.pk}/",
            {"status": 999999},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        application.refresh_from_db()
        self.assertEqual(application.status, self.applied_status)

    def test_application_creation_remains_atomic_when_attribute_save_fails(self):
        attribute = Attribute.objects.create(name="GPA", data_type=Attribute.DataType.DECIMAL)
        JobAttribute.objects.create(job=self.job, attribute=attribute, required=True)

        with patch(
            "job.views.StudentAttributeValue.objects.update_or_create",
            side_effect=RuntimeError("simulated profile value failure"),
        ):
            response = self.client.post(
                "/job/applications/",
                {
                    "job": self.job.pk,
                    "resume_id": self.resume.pk,
                    "answers": {str(attribute.pk): "3.8"},
                },
                format="json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Application.objects.filter(student=self.student, job=self.job).exists())
        self.assertEqual(ApplicationAttributeValue.objects.count(), 0)
        self.assertEqual(StudentAttributeValue.objects.count(), 0)


class ApplicationStatusMigrationTests(TransactionTestCase):
    migrate_from = [("job", "0020_alter_attribute_data_type")]
    migrate_to = [("job", "0021_application_status")]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        JobModel = old_apps.get_model("job", "Job")
        ApplicationModel = old_apps.get_model("job", "Application")

        student_user = User.objects.create_user(
            username="migration-student",
            email="migration-student@example.com",
            password="password",
            role="student",
        )
        company_user = User.objects.create_user(
            username="migration-company",
            email="migration-company@example.com",
            password="password",
            role="company",
        )
        course = Course.objects.create(name="Migration Course", semester=1, years=4)
        batch = Batch.objects.create(
            course=course,
            start_year=2025,
            end_year=2029,
        )
        student = Student.objects.create(user=student_user, batch=batch)
        company = Company.objects.create(user=company_user, name="Migration Company")
        job = Job.objects.create(
            company=company,
            batch=batch,
            title="Migration Job",
            description="Test migration",
            location="Remote",
        )
        self.application_id = ApplicationModel.objects.create(
            student_id=student.pk,
            job_id=job.pk,
            status="Rejected",
        ).pk

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.Application = Application

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_application_status_value_is_preserved(self):
        application = self.Application.objects.get(pk=self.application_id)

        self.assertEqual(application.status.name, "Rejected")
        self.assertEqual(application.status.code, "rejected")
