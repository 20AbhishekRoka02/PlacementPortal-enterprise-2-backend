from django.contrib import admin
from company.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("name", "hr_email", "website", "hr_phone_number")
    search_fields = ("name", "hr_email")

admin.site.register(Company, CompanyAdmin)
