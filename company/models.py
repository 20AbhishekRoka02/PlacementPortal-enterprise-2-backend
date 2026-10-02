from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    hr_phone_number = models.CharField(max_length=20, blank=True)
    hr_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name
