from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


def copy_user_email_to_hr_email(apps, schema_editor):
    Company = apps.get_model("company", "Company")
    companies = Company.objects.filter(user__isnull=False).values_list(
        "pk", "user__email"
    )
    for company_id, user_email in companies.iterator():
        Company.objects.filter(pk=company_id).update(hr_email=user_email)


def restore_company_user_links(apps, schema_editor):
    Company = apps.get_model("company", "Company")
    User = apps.get_model("users", "User")

    for company_id, hr_email in Company.objects.values_list("pk", "hr_email").iterator():
        user = User.objects.filter(email=hr_email).first()
        if user is None:
            raise RuntimeError(
                f"Cannot restore the user for company {company_id}: "
                "no account matches its current hr_email."
            )
        Company.objects.filter(pk=company_id).update(user_id=user.pk)


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0002_alter_company_user"),
        ("users", "0002_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="user",
            field=models.OneToOneField(
                limit_choices_to=models.Q(("role", "company")),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="company_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            copy_user_email_to_hr_email,
            restore_company_user_links,
        ),
        migrations.RemoveField(
            model_name="company",
            name="user",
        ),
    ]
