from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    UNIVERSITY = "university", "University"
    STUDENT = "student", "Student"
    COMPANY = "company", "Company"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email