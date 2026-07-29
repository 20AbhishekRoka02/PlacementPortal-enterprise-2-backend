from django.db import models, transaction
from ckeditor.fields import RichTextField
from course.models import Batch
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from job.helpers import file_size_in_kbs
from decimal import Decimal
from student.models import Student
import os
from configs.helpers import get_resume_config

# Create your models here.
class Job(models.Model):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='jobs')
    title = models.TextField()
    description = RichTextField()
    location = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)


class Resume(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, related_name='resumes')
    size = models.DecimalField(max_digits=6, decimal_places=2, default=0.0,  validators=[
            MaxValueValidator(Decimal('20.00')) # maximum allowed value
        ])
    file_name = models.TextField(blank=True, null=True, default="")
    file = models.FileField(upload_to="resumes/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])])
    detail = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        resume_conf = get_resume_config()
        max_resumes = resume_conf.max_number_of_resumes
        if self.file is None:
            raise ValidationError({
                'file': "You have to upload a file."
                })
        if self.pk is None:
            with transaction.atomic():
                student_locked = (
                    Student
                    .objects.select_for_update()
                    .get(pk=self.student.pk)
                )
                # 2. Inside the lock, safe to count accurately
                existing_count = Resume.objects.filter(student=student_locked).count()

                if existing_count >= max_resumes: # Resume count
                    raise ValidationError({
                        'file': f"You cannot upload more than {max_resumes} resumes."
                    })

            if file_size_in_kbs(self.file.size) > Decimal('20.00'):
                raise ValidationError({
                    'size': "You cannot uploade file size more than 20 KB"
                })

        if self.size > Decimal('20.00'):
            raise ValidationError({
                'size': "You cannot uploade file size more than 20 KB"
                })

    def save(self, *args, **kwargs):
        resume_conf = get_resume_config()
        max_resumes = resume_conf.max_number_of_resumes
        if Resume.objects.filter(student=self.student).count() < max_resumes: # resume count
            self.size = file_size_in_kbs(self.file.size)
            self.file_name = self.file.name
            self.full_clean()
            return super().save(*args, **kwargs)
        else:
            raise Exception(f"Students cannot have more than {max_resumes} resumes")
    
    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        NOT_APPLIED = "Not Applied", ("Not Applied")
        APPLIED = "Applied", ("Applied")
        REJECTED = "Rejected", ("Rejected")
        PLACED = "Placed", ("Placed")

    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    status = models.CharField(
        max_length=255,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    # Snapshots
    job_title = models.TextField(default="")
    job_description = RichTextField(default="")
    job_location = models.CharField(max_length=255, default="")
    job_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    student_phone_number = models.CharField(max_length=20, blank=True)
    student_whatsapp_number = models.CharField(max_length=20, blank=True)
    student_email_id = models.EmailField(max_length=254, null=True, blank=True)
    resume_detail = RichTextField(default="")

    def __str__(self):
        return f"{self.student.user.email} applied for {self.job.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'job'],
                name='unique_student_job'  # Must be unique in DB
            )
        ]
