from django.contrib import admin
from job.models import (
    Job,
)
# Register your models here.
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company__name', 'salary', 'location', 'deadline', 'created_at', 'updated_at')

admin.site.register(Job, JobAdmin)