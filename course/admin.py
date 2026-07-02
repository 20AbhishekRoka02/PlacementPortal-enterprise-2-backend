from django.contrib import admin
from course.models import (
    Course,
    Batch,
)
# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("pk", "name", "semester", "years", "created_at", "updated_at")

class BatchAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("pk", "name", "course__name", "start_year", "end_year", "created_at", "updated_at")


admin.site.register(Course, CourseAdmin)
admin.site.register(Batch, BatchAdmin)