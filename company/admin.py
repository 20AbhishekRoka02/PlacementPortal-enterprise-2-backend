from django.contrib import admin
from company.models import (
    Company,
)
from django.shortcuts import redirect
# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("name", "get_company_email", "website", "hr_phone_number", "hr_email")
    list_filter = ("user",)
    
    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).filter(
            
            user=request.user
        )

    def get_company_email(self, obj):
        return obj.user.email

    get_company_email.short_description = "email"
    
    def changelist_view(self, request, extra_context=None):

        if request.user.is_superuser:

            return super().changelist_view(
                request,
                extra_context
            )

        company = request.user.company_profile

        return redirect(
            f"/admin/company/company/{company.pk}/change/"
        )
    
    def get_fieldsets(self, request, obj=None):

        # Superuser
        if request.user.is_superuser:
            return (
                (
                    "Company Information",
                    {
                        "fields": (
                            "user",
                            "name",
                            "website"
                        )
                    },
                ),
                (
                    "HR Information",
                    {
                        "fields": (
                            "hr_email",
                            "hr_phone_number",
                        )
                    },
                ),
            )

        # Company user
        return (
            (
                "My Profile",
                {
                    "fields": (
                        "name",
                        "website",
                    )
                },
            ),
            (
                "Contact Information",
                {
                    "fields": (
                        "hr_email",
                        "hr_phone_number",
                    )
                },
            ),
        )

admin.site.register(Company, CompanyAdmin)
