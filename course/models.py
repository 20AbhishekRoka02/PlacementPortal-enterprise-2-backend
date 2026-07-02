from django.db import models

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    semester = models.IntegerField()
    years = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# A batch will include course name and the batch number
class Batch(models.Model):
    name = models.CharField(max_length=255,  blank=True, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches', default=None)
    start_year = models.PositiveIntegerField(default=0)
    end_year = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.course.name}-{self.start_year}-{self.end_year}"
        super().save(*args, **kwargs)