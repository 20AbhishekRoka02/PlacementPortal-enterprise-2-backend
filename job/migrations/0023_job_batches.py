from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0022_applicationexport_progress"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="batch",
        ),
        migrations.AddField(
            model_name="job",
            name="batches",
            field=models.ManyToManyField(
                related_name="jobs",
                to="course.batch",
            ),
        ),
    ]