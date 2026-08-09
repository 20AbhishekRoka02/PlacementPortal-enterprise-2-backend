from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# Create your models here.
class Student(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='student_profile')
    # phone_number = models.CharField(max_length=20, blank=True)
    # whatsapp_number = models.CharField(max_length=20, blank=True)
    # tenth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[
    #     MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))
    # ])
    # twelfth_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[
    #     MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))
    # ])
    # cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, validators=[
    #     MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('10.00'))
    # ])
    batch = models.ForeignKey('course.Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.user.email
