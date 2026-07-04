from rest_framework import serializers
from job.models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['company', 'title', 'location', 'salary', 'deadline', 'batch']
