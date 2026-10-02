from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from company.models import Company
from course.models import Batch, Course
from job.models import Job
from users.models import User, UserRole


class CompanyApiTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="company-api-staff",
            email="company-api-staff@example.com",
            password="password",
            role=UserRole.PLACEMENT_OFFICER,
        )
        self.student_user = User.objects.create_user(
            username="company-api-student",
            email="company-api-student@example.com",
            password="password",
            role=UserRole.STUDENT,
        )
        self.company = Company.objects.create(
            name="Existing Company",
            hr_email="hr@existing.example.com",
        )

    def test_staff_can_list_retrieve_and_create_companies(self):
        self.assertNotIn(
            "user",
            {field.name for field in Company._meta.get_fields()},
        )
        client = APIClient()
        client.force_authenticate(self.staff_user)

        list_response = client.get("/company/companies/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data[0]["id"], self.company.pk)
        self.assertNotIn("user", list_response.data[0])

        detail_response = client.get(f"/company/companies/{self.company.pk}/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data["name"], "Existing Company")

        create_response = client.post(
            "/company/companies/",
            {
                "name": "Created Company",
                "website": "https://created.example.com",
                "hr_email": "hr@created.example.com",
                "hr_phone_number": "1234567890",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data["name"], "Created Company")
        self.assertNotIn("user", create_response.data)

    def test_company_api_rejects_students_and_users_without_a_role(self):
        student_client = APIClient()
        student_client.force_authenticate(self.student_user)
        student_get = student_client.get("/company/companies/")
        student_post = student_client.post(
            "/company/companies/",
            {"name": "Student Company"},
            format="json",
        )

        legacy_company_client = APIClient()
        legacy_company_client.force_authenticate(
            User.objects.create_user(
                username="legacy-company",
                email="legacy-company@example.com",
                password="password",
                role=None,
                is_staff=False,
            )
        )
        legacy_response = legacy_company_client.get("/company/companies/")

        self.assertEqual(student_get.status_code, 403)
        self.assertEqual(student_post.status_code, 403)
        self.assertEqual(legacy_response.status_code, 403)
        self.assertFalse(Company.objects.filter(name="Student Company").exists())

    def test_company_api_requires_authentication(self):
        response = APIClient().get("/company/companies/")
        self.assertIn(response.status_code, (401, 403))


class CompanyGroupSetupTests(TestCase):
    def test_setup_groups_does_not_recreate_company_group(self):
        call_command("setup_groups")
        self.assertFalse(Group.objects.filter(name="Company").exists())


class CompanyUserRemovalMigrationTests(TransactionTestCase):
    migrate_from = [
        ("company", "0002_alter_company_user"),
        ("users", "0002_alter_user_role"),
    ]
    migrate_to = [
        ("company", "0003_remove_company_user"),
        ("users", "0003_remove_company_role"),
    ]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        UserModel = old_apps.get_model("users", "User")
        CompanyModel = old_apps.get_model("company", "Company")
        GroupModel = old_apps.get_model("auth", "Group")
        self.user_id = UserModel.objects.create(
            username="legacy-company",
            email="legacy-company@example.com",
            password="password",
            role="company",
            is_staff=True,
            is_active=True,
        ).pk
        group, _ = GroupModel.objects.get_or_create(name="Company")
        user = UserModel.objects.get(pk=self.user_id)
        user.groups.add(group)
        company = CompanyModel.objects.create(
            user_id=self.user_id,
            name="Legacy Company",
            hr_email="old-hr@example.com",
        )
        self.company_id = company.pk

        course = Course.objects.create(name="Migration Course", semester=1, years=4)
        batch = Batch.objects.create(course=course, start_year=2025, end_year=2029)
        self.job_id = Job.objects.create(
            company_id=company.pk,
            batch=batch,
            title="Legacy Company Job",
            description="Existing job remains linked",
            location="Remote",
        ).pk

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_migration_preserves_accounts_company_ids_and_job_relations(self):
        company = Company.objects.get(pk=self.company_id)
        user = User.objects.get(pk=self.user_id)
        job = Job.objects.get(pk=self.job_id)

        self.assertEqual(company.hr_email, "legacy-company@example.com")
        self.assertEqual(job.company_id, self.company_id)
        self.assertEqual(user.role, None)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(Group.objects.filter(name="Company").exists())
        self.assertEqual(User.objects.filter(pk=self.user_id).count(), 1)
