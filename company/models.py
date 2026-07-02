from django.db import models
from users.models import User, UserRole
from django.db.models import Q
# Create your models here.

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to=Q(role=UserRole.COMPANY), related_name='company_profile')
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    hr_phone_number = models.CharField(max_length=20, blank=True)
    hr_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name