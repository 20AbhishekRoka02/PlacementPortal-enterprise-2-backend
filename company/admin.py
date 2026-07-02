from django.contrib import admin
from company.models import (
    Company,
)

# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("name", "get_company_email", "website", "hr_phone_number", "hr_email")
    list_filter = ("user",)

    def get_company_email(self, obj):
        return obj.user.email

    get_company_email.short_description = "email"

admin.site.register(Company, CompanyAdmin)
