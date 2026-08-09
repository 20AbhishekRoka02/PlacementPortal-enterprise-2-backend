from django.utils.html import format_html
from django.contrib import admin
from job.models import (
    Job,
    Application,
    Resume,
    Attribute,
    JobAttribute,
    ApplicationAttributeValue,
    StudentAttributeValue
)
from users.models import UserRole
# Register your models here.
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "data_type")
    search_fields = ("name",)


class JobAttributeInline(admin.TabularInline):
    model = JobAttribute
    extra = 1
    autocomplete_fields = ("attribute",)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company__name', 'salary', 'location', 'deadline', 'created_at', 'updated_at')
    inlines = [JobAttributeInline]
    def get_queryset(self, request):
        if request.user.role == UserRole.COMPANY:
            return super().get_queryset(request).filter(
                company=request.user.company_profile
            )
            
        return super().get_queryset(request)


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
    inlines = [ApplicationAttributeInline]

    def get_queryset(self, request):
        if request.user.role == UserRole.COMPANY:
            return super().get_queryset(request).filter(
                job__company=request.user.company_profile
            )
            
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
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(StudentAttributeValue)
