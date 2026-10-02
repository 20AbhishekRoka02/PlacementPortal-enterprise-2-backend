from django.db import migrations, models


def remove_company_role_and_group(apps, schema_editor):
    User = apps.get_model("users", "User")
    Group = apps.get_model("auth", "Group")

    User.objects.filter(role="company").update(role=None, is_staff=False)
    Group.objects.filter(name="Company").delete()


def restore_company_role_and_group_memberships(apps, schema_editor):
    User = apps.get_model("users", "User")
    Company = apps.get_model("company", "Company")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    company_emails = list(Company.objects.values_list("hr_email", flat=True))
    company_users = User.objects.filter(
        email__in=company_emails,
        role__isnull=True,
        is_staff=False,
    )
    if any(not email for email in company_emails) or company_users.count() != len(
        company_emails
    ):
        raise RuntimeError(
            "Cannot restore Company roles safely: not every Company email "
            "maps uniquely to a former Company user."
        )

    company_users.update(role="company", is_staff=True)

    group, _ = Group.objects.get_or_create(name="Company")
    for user in company_users.iterator():
        user.groups.add(group)

    company_permission_specs = [
        ("job", "job", ["add_job", "change_job", "view_job", "delete_job"]),
        ("job", "application", ["view_application"]),
        ("company", "company", ["view_company", "change_company"]),
    ]
    permissions = Permission.objects.none()
    for app_label, model_name, codenames in company_permission_specs:
        content_type = ContentType.objects.filter(
            app_label=app_label,
            model=model_name,
        ).first()
        if content_type:
            permissions = permissions | Permission.objects.filter(
                content_type=content_type,
                codename__in=codenames,
            )
    group.permissions.set(permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0003_remove_company_user"),
        ("users", "0002_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(
            remove_company_role_and_group,
            restore_company_role_and_group_memberships,
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("admin", "Admin"),
                    ("university", "University"),
                    ("student", "Student"),
                    ("placement_officer", "Placement Officer"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
