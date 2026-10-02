from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify
import job.models


LEGACY_STATUS_NAMES = (
    "Not Applied",
    "Applied",
    "Rejected",
    "Placed",
)


def _get_or_create_status(Status, name, database):
    manager = Status.objects.using(database)
    status = manager.filter(name=name).first()
    if status:
        return status

    base_code = slugify(name) or "legacy-status"
    code = base_code[:255]
    suffix = 2
    while manager.filter(code=code).exists():
        suffix_text = f"-{suffix}"
        code = f"{base_code[:255 - len(suffix_text)]}{suffix_text}"
        suffix += 1

    return manager.create(name=name, code=code)


def populate_application_statuses(apps, schema_editor):
    Application = apps.get_model("job", "Application")
    ApplicationStatus = apps.get_model("job", "ApplicationStatus")
    database = schema_editor.connection.alias

    for name in LEGACY_STATUS_NAMES:
        _get_or_create_status(ApplicationStatus, name, database)

    legacy_names = (
        Application.objects.using(database)
        .order_by()
        .values_list("status", flat=True)
        .distinct()
    )
    for name in legacy_names:
        if not name:
            continue
        status = _get_or_create_status(ApplicationStatus, name, database)
        Application.objects.using(database).filter(status=name).update(status_ref_id=status.pk)


def restore_application_statuses(apps, schema_editor):
    Application = apps.get_model("job", "Application")
    ApplicationStatus = apps.get_model("job", "ApplicationStatus")
    database = schema_editor.connection.alias

    for application in (
        Application.objects.using(database)
        .exclude(status_ref_id=None)
        .values_list("pk", "status_ref_id")
        .iterator()
    ):
        application_id, status_id = application
        name = ApplicationStatus.objects.using(database).get(pk=status_id).name
        Application.objects.using(database).filter(pk=application_id).update(status=name)

    Application.objects.using(database).filter(status_ref_id=None).update(status="")


class Migration(migrations.Migration):

    dependencies = [
        ("job", "0020_alter_attribute_data_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApplicationStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("code", models.SlugField(editable=False, max_length=255, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="application",
            name="status_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="applications",
                to="job.applicationstatus",
            ),
        ),
        migrations.RunPython(
            populate_application_statuses,
            restore_application_statuses,
        ),
        migrations.RemoveField(
            model_name="application",
            name="status",
        ),
        migrations.RenameField(
            model_name="application",
            old_name="status_ref",
            new_name="status",
        ),
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.ForeignKey(
                blank=True,
                default=job.models.default_application_status_id,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="applications",
                to="job.applicationstatus",
            ),
        ),
    ]
