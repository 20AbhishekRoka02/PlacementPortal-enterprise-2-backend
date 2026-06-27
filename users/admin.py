from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User, UserRole
# from company.models import Company
# from student.models import Student
# Register your models here.

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'role')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Role Management",
            {
                "fields": ("role",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.username:
            obj.username = obj.email
        if obj.role in [UserRole.ADMIN, UserRole.UNIVERSITY, UserRole.COMPANY]:
            if obj.role == UserRole.ADMIN:
                obj.is_superuser = True
            obj.is_staff = True

        super().save_model(request, obj, form, change)

        # if obj.role == UserRole.COMPANY:
        #     Company.objects.get_or_create(user=obj)

        # elif obj.role == UserRole.STUDENT:
        #     Student.objects.get_or_create(user=obj)

admin.site.register(User, UserAdmin)