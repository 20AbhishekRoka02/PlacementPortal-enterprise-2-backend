from django.contrib import admin
from student.models import Student

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ["pk", "user__first_name", "user__last_name", "phone_number", "batch"]

admin.site.register(Student, StudentAdmin)
