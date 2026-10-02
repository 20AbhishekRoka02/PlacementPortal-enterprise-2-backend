from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from users.models import User, UserRole
from student.models import Student
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
        if obj.role in [UserRole.ADMIN, UserRole.UNIVERSITY, UserRole.PLACEMENT_OFFICER]:
            if obj.role in [UserRole.ADMIN, UserRole.UNIVERSITY]:
                obj.is_superuser = True
            obj.is_staff = True

        super().save_model(request, obj, form, change)

        if obj.role == UserRole.PLACEMENT_OFFICER:
            placement_officer_group, _ = Group.objects.get_or_create(name='Placement_Officer')
            obj.groups.add(placement_officer_group)

        elif obj.role == UserRole.STUDENT:
            Student.objects.get_or_create(user=obj)

admin.site.register(User, UserAdmin)
