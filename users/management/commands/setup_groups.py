from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from job.models import Job, Application, Resume

class Command(BaseCommand):
    help = 'Create user groups with permissions'
    
    def handle(self, *args, **options):
        # Create groups
        placement_officer_group, created = Group.objects.get_or_create(name="Placement_Officer")
        
        # Get permissions
        job_content_type = ContentType.objects.get_for_model(Job)
        application_content_type = ContentType.objects.get_for_model(Application)
        resume_content_type = ContentType.objects.get_for_model(Resume)

        # Placement Officer permission on their own job post
        placement_officer_permissions = Permission.objects.filter(
            content_type=job_content_type,
            codename__in=['add_job', 'change_job', 'view_job', 'delete_job']
        ) | Permission.objects.filter(
            content_type=application_content_type,
            codename__in=['view_application', 'change_application']
        ) | Permission.objects.filter(
            content_type=resume_content_type,
            codename__in=['view_resume']
        ) 
        placement_officer_group.permissions.set(placement_officer_permissions)
        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and permissions')
        )
