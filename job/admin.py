from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.db.models import Count
from job.models import (
    Job,
    Application,
    ApplicationStatus,
    Resume,
    Attribute,
    JobAttribute,
    ApplicationAttributeValue,
    StudentAttributeValue,
    ApplicationExport
)
from .tasks import generate_application_export
# Register your models here.
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "data_type")
    search_fields = ("name",)


class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    readonly_fields = ("code",)
    search_fields = ("name",)


class JobAttributeInline(admin.TabularInline):
    model = JobAttribute
    extra = 1
    autocomplete_fields = ("attribute",)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company__name', 'salary', 'location', 'deadline', "application_count", 'created_at', 'updated_at', "view_applications")
    actions = ["export_application_data"]
    inlines = [JobAttributeInline]
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _application_count=Count("applications")
        )
    
    def application_count(self, obj):
        return obj._application_count
    
    def view_applications(self, obj):
        url = reverse(
            "admin:job_application_changelist"
        )

        url += f"?job__id__exact={obj.pk}"

        return format_html(
            '<a href="{}">View applications</a>',
            url,
        )

    # Actions
    @admin.action(description="Export Application of given Job")
    def export_application_data(self, request, queryset):
        # Only one job can be exported at a time.
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one job to export.",
                level=messages.ERROR,
            )
            return
        job = queryset.first()

        export = ApplicationExport.objects.create(
            requested_by=request.user,
            status=ApplicationExport.Status.PENDING,
        )

        export.jobs.add(job)

        task = generate_application_export.delay(export.pk)
        print("Task id: ", task.id)

        self.message_user(
            request,
            f"Export for '{job.title}' has been queued. "
            f"You can monitor it from the Exports section.",
            level=messages.SUCCESS,
        )

class ResumeAdmin(admin.ModelAdmin):
    list_display = ("pk", "student__user__email", "file_name", "size", "file", 'created_at', 'updated_at')



class ApplicationAttributeInline(admin.TabularInline):
    model = ApplicationAttributeValue
    extra = 0
    can_delete = False

    readonly_fields = (
        "attribute_name",
        "data_type",
        "required",
        "value",
    )


class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = (
        "view_resume",
    )
    list_display = ["student__user__first_name", "student__user__last_name", "student_email_id", "job_title", "status", "view_resume"]
    inlines = [ApplicationAttributeInline]

    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def view_resume(self, obj):

        if obj.resume:
            return format_html(
                '<a href="/application/{}/resume/" target="_blank">View Resume</a>',
                obj.id
            )

        return "No Resume Uploaded"

    view_resume.short_description = "Resume"


class StudentAttributeValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StudentAttributeValue._meta.get_fields()]

admin.site.register(Job, JobAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationStatus, ApplicationStatusAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(StudentAttributeValue)
admin.site.register(ApplicationAttributeValue)
admin.site.register(ApplicationExport)
