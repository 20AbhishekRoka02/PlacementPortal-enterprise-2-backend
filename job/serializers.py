from rest_framework import serializers
from job.models import Job, Application, Resume
from job.helpers import file_size_in_kbs
from decimal import Decimal
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


class ApplicationDetailSerializer(ApplicationListSerializer):
    resume_file_name = serializers.SerializerMethodField(read_only=True, method_name="get_resume_file_name")
    resume_file_size = serializers.SerializerMethodField(read_only=True, method_name="get_resume_file_size")
    
    class Meta(ApplicationListSerializer.Meta):
        fields = ApplicationListSerializer.Meta.fields + [
            'job_title', 'job_description', 'job_location', 'job_salary', 'student_phone_number', 
            'student_whatsapp_number', 'student_email_id', 'resume_file_name', 'resume_file_size']
    
    def get_resume_file_name(self, obj):
        resume = obj.resume
        if resume:
            return resume.file_name
        return ""
    
    def get_resume_file_size(self, obj):
        resume = obj.resume
        if resume:
            return resume.size
        return Decimal("0.0")


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"
        

class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"


class ResumeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "size", "file_name", "file"]
    
    def validate_file(self, file):
        if file.size > 20 * 1024:
            raise serializers.ValidationError(
                "Resume cannot be larger than 20 KB."
            )

        if not file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF resumes are allowed."
            )
        return file

    def create(self, validated_data):
        request = self.context.get("request")
        uploaded_file = validated_data["file"]
        return Resume.objects.create(
            student=request.user.student_profile,
            size=file_size_in_kbs(uploaded_file.size),
            file_name=uploaded_file.name,
            **validated_data
        )
