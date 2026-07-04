from django.db import models

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='student_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    batch = models.ForeignKey('course.Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.user.email

# class Resume(models.Model):
#     student = models.OneToOneField(
#         'student.Student',
#         on_delete=models.CASCADE,
#         related_name='resume'
#     )

#     # Basic Info
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)

#     # JSON Sections
#     social_media = models.JSONField(default=list, blank=True)
#     education = models.JSONField(default=list, blank=True)
#     experience = models.JSONField(default=list, blank=True)
#     projects = models.JSONField(default=list, blank=True)

#     # Misc Section
#     misc_title = models.CharField(max_length=255, blank=True)
#     misc_description = models.TextField(blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.name} Resume"
