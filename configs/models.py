from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class ResumeConfig(models.Model):
    max_resume_size = models.DecimalField(max_digits=6, decimal_places=2, default=20.00, validators=[
        MinValueValidator(Decimal('0.00'))
    ])