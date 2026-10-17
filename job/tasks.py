# tasks.py
import io
import os
import zipfile

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from openpyxl import Workbook

from .models import ApplicationExport, Application


@shared_task
def generate_application_export(export_id):
    export = ApplicationExport.objects.get(pk=export_id)

    export.status = ApplicationExport.Status.PROCESSING
    export.current_step = ApplicationExport.Step.BUILDING_SPREADSHEET
    export.started_at = timezone.now()
    export.save(update_fields=["status", "current_step", "started_at"])

    try:
        jobs = export.jobs.all()

        # We currently allow only one job per export.
        if jobs.count() != 1:
            raise ValueError(
                "An application export must contain exactly one job."
            )

        job = jobs.first()
        job_attributes = job.attributes.all()

        applications = list(
            Application.objects
            .filter(job=job)
            .select_related(
                "student__user",
                "resume",
            )
            .prefetch_related(
                "attributes"
            )
        )

        resumes_to_export = [
            application.resume
            for application in applications
            if application.resume and application.resume.file
        ]
        export.total_applications = len(applications)
        export.total_resumes = len(resumes_to_export)
        export.save(update_fields=["total_applications", "total_resumes"])

        excel_buffer = io.BytesIO()

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Applications"

        # TODO:
        # Replace these with your actual fixed Application/Student fields.
        headers = [
            "Student Name",
            "Email",
        ]
        
        headers.extend([attribute.attribute.name for attribute in job_attributes])
        

        worksheet.append(headers)

        application_count = 0
        resume_count = 0

        for application in applications:
            answers = {
                answer.attribute_name: answer.value 
                for answer in application.attributes.all() 
            }

            student = application.student
            
            row = [
                student.user.get_full_name(),
                student.user.email,
            ]
            
            for job_attribute in job_attributes:

                attribute_name = job_attribute.attribute.name

                row.append(
                    answers.get(attribute_name, "")
            )
            
            worksheet.append(row)

            application_count += 1
            export.processed_applications = application_count
            export.progress_percentage = (
                int(application_count * 30 / export.total_applications)
                if export.total_applications else 30
            )
            export.save(
                update_fields=["processed_applications", "progress_percentage"]
            )

        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        # ---------------------------------------------------------
        # Create ZIP
        # ---------------------------------------------------------

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:

            # Add Excel file
            zip_file.writestr(
                "applications.xlsx",
                excel_buffer.getvalue(),
            )

            export.current_step = ApplicationExport.Step.ADDING_RESUMES
            export.progress_percentage = 30
            export.save(update_fields=["current_step", "progress_percentage"])

            # Add resumes
            for application in applications:
                resume = application.resume

                if not resume or not resume.file:
                    continue

                try:
                    resume.file.open("rb")

                    filename = os.path.basename(
                        resume.file.name
                    )

                    # Avoid filename collisions
                    filename = (
                        f"{application.student.pk}_{filename}"
                    )

                    zip_file.writestr(
                        f"resumes/{filename}",
                        resume.file.read(),
                    )

                    resume_count += 1
                    export.processed_resumes += 1
                    export.progress_percentage = 30 + (
                        int(export.processed_resumes * 65 / export.total_resumes)
                        if export.total_resumes else 65
                    )
                    export.save(
                        update_fields=["processed_resumes", "progress_percentage"]
                    )

                finally:
                    resume.file.close()

        zip_buffer.seek(0)

        filename = (
            f"{slugify(job.title)}-applications-"
            f"{timezone.now().strftime('%Y%m%d-%H%M%S')}.zip"
        )

        export.current_step = ApplicationExport.Step.FINALIZING
        export.progress_percentage = 95
        export.save(update_fields=["current_step", "progress_percentage"])

        export.file.save(
            filename,
            ContentFile(zip_buffer.getvalue()),
            save=False,
        )

        export.application_count = application_count
        export.resume_count = resume_count
        export.status = ApplicationExport.Status.COMPLETED
        export.current_step = ApplicationExport.Step.COMPLETED
        export.progress_percentage = 100
        export.completed_at = timezone.now()

        export.save(
            update_fields=[
                "file",
                "application_count",
                "resume_count",
                "status",
                "current_step",
                "progress_percentage",
                "completed_at",
            ]
        )

    except Exception as exc:
        export.status = ApplicationExport.Status.FAILED
        export.current_step = ApplicationExport.Step.FAILED
        export.error_message = str(exc)
        export.completed_at = timezone.now()

        export.save(
            update_fields=[
                "status",
                "current_step",
                "error_message",
                "completed_at",
            ]
        )

        raise
