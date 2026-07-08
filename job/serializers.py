from rest_framework import serializers
from job.models import Job, Application
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class JobListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True, method_name="get_id")
    company = serializers.SerializerMethodField(read_only=True, method_name="get_company_name")
    batch = serializers.SerializerMethodField(read_only=True, method_name="get_batch_name")
    status = serializers.SerializerMethodField(read_only=True, method_name="get_application_status")
    class Meta:
        model = Job
        fields = ['id', 'company', 'title', 'location', 'salary', 'deadline', 'batch', 'status']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["student"] = self.request.user.student_profile.first()
        return context

    def get_id(self, obj):
        return obj.pk

    def get_company_name(self, obj):
        return obj.company.name

    def get_batch_name(self, obj):
        return obj.batch.name

    def get_application_status(self, obj):
        student = None
        request = self.context.get("request")
        if request:
            student = request.user.student_profile
        if student:
            applications = Application.objects.filter(
                student=student,
                job=obj
            )
            print("applications: ", applications)
            if applications.exists():
                return applications.first().status
        return Application.ApplicationStatus.NOT_APPLIED

class JobDetailSerializer(JobListSerializer):
    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + ['description']


class ApplicationListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True, method_name="get_application_id")
    title = serializers.SerializerMethodField(read_only=True, method_name="get_job_title")
    company = serializers.SerializerMethodField(read_only=True, method_name="get_company_name")
    class Meta:
        model = Application
        fields = ["id", "title", "company", "status", "applied_at"]

    def get_application_id(self, obj):
        return obj.pk

    def get_job_title(self, obj):
        return obj.job.title

    def get_company_name(self, obj):
        return obj.job.company.name
