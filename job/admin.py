from django.contrib import admin
from job.models import (
    Job,
    Resume
)
# Register your models here.
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company__name', 'salary', 'location', 'deadline', 'created_at', 'updated_at')


class ResumeAdmin(admin.ModelAdmin):
    list_display = ("pk", "student__user__email", "file_name", "size", "file")

admin.site.register(Job, JobAdmin)
admin.site.register(Resume, ResumeAdmin)