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