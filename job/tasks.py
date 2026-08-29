# tasks.py
import io
import os
import zipfile
from datetime import datetime

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
    export.started_at = timezone.now()
    export.save(update_fields=["status", "started_at"])

    try:
        jobs = export.jobs.all()

        # We currently allow only one job per export.
        if jobs.count() != 1:
            raise ValueError(
                "An application export must contain exactly one job."
            )

        job = jobs.first()
        job_attributes = job.attributes.all()

        applications = (
            Application.objects
            .filter(job=job)
            .select_related(
                "student",
                "resume",
            )
            .prefetch_related(
                "attributes"
            )
        )

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

                finally:
                    resume.file.close()

        zip_buffer.seek(0)

        filename = (
            f"{slugify(job.title)}-applications-"
            f"{timezone.now().strftime('%Y%m%d-%H%M%S')}.zip"
        )

        export.file.save(
            filename,
            ContentFile(zip_buffer.getvalue()),
            save=False,
        )

        export.application_count = application_count
        export.resume_count = resume_count
        export.status = ApplicationExport.Status.COMPLETED
        export.completed_at = timezone.now()

        export.save(
            update_fields=[
                "file",
                "application_count",
                "resume_count",
                "status",
                "completed_at",
            ]
        )

    except Exception as exc:
        export.status = ApplicationExport.Status.FAILED
        export.error_message = str(exc)
        export.completed_at = timezone.now()

        export.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
            ]
        )

        raise