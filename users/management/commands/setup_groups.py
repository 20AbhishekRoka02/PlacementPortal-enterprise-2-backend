from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from job.models import Job, Application
from company.models import Company

class Command(BaseCommand):
    help = 'Create user groups with permissions'
    
    def handle(self, *args, **options):
        # Create groups
        company_group, created = Group.objects.get_or_create(name="Company")
        
        # Get permissions
        job_content_type = ContentType.objects.get_for_model(Job)
        application_content_type = ContentType.objects.get_for_model(Application)
        company_content_type = ContentType.objects.get_for_model(Company)
        
        # Company permission on their own job post
        company_permissions = Permission.objects.filter(
            content_type=job_content_type,
            codename__in=['add_job', 'change_job', 'view_job', 'delete_job']
        ) | Permission.objects.filter(
            content_type=application_content_type,
            codename__in=['view_application']
        ) | Permission.objects.filter(
            content_type=company_content_type,
            codename__in=['view_company', 'change_company']
        )
        company_group.permissions.set(company_permissions)
        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and permissions')
        )
        
        
        
        