from django.db import models
from ckeditor.fields import RichTextField
from course.models import Batch

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

class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        NOT_APPLIED = "Not Applied", ("Not Applied")
        APPLIED = "Applied", ("Applied")
        REJECTED = "Rejected", ("Rejected")
        PLACED = "Placed", ("Placed")

    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
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
    student_email_id = models.EmailField(max_length=254, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.email} applied for {self.job.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'job'],
                name='unique_student_job'  # Must be unique in DB
            )
        ]
