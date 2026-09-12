from rest_framework import serializers
from job.models import Job, Application, Resume, StudentAttributeValue, ApplicationAttributeValue
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


class JobAdminListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True, method_name="get_id")
    company = serializers.SerializerMethodField(read_only=True, method_name="get_company_name")
    batch = serializers.SerializerMethodField(read_only=True, method_name="get_batch_name")
    applicants_count = serializers.SerializerMethodField(read_only=True, method_name="get_applicants_count")
    published_on = serializers.SerializerMethodField(read_only=True, method_name="get_published_on")

    class Meta:
        model = Job
        fields = ['id', 'company', 'title', 'location', 'salary', 'deadline', 'batch', 'applicants_count', 'published_on']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def get_id(self, obj):
        return obj.pk

    def get_company_name(self, obj):
        return obj.company.name

    def get_batch_name(self, obj):
        return obj.batch.name

    def get_published_on(self, obj):
        return obj.created_at
    
    def get_applicants_count(self, obj):
        return obj.applications.count()


class JobDetailSerializer(JobListSerializer):
    attributes = serializers.SerializerMethodField(read_only=True, method_name="get_attributes")
    
    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + ['description', 'attributes']
    
    def get_attributes(self, obj):
        student = self.context.get("student")
        attributes_list = list()
        attributes = obj.attributes
        if attributes.exists():
            for job_attribute in attributes.all():
                sav = StudentAttributeValue.objects.filter(student=student, attribute=job_attribute.attribute)
                value = None
                if sav.exists():
                    value = sav.first().value.get('value')
                attributes_list.append({
                    "pk": job_attribute.attribute.pk,
                    "name": job_attribute.attribute.name,
                    "data_type": job_attribute.attribute.data_type,
                    "required": job_attribute.required,
                    "order": job_attribute.order,
                    "value": value
                })
            return attributes_list
        return None

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


class ApplicationAdminListSerializer(serializers.ModelSerializer):
    from student.serializers import StudentProfileSerializer
    id = serializers.SerializerMethodField(read_only=True, method_name="get_application_id")
    student = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = ["id", "student", "status", "applied_at"]

    def get_application_id(self, obj):
        return obj.pk


class JobAdminDetailSerializer(JobAdminListSerializer):
    attributes = serializers.SerializerMethodField(read_only=True, method_name="get_attributes")
    # applications = serializers.SerializerMethodField(read_only=True, method_name="get_applications")
    applications = ApplicationAdminListSerializer(many=True, read_only=True)
    
    class Meta(JobAdminListSerializer.Meta):
        fields = JobAdminListSerializer.Meta.fields + ['description', 'attributes', 'applications']
    
    def get_attributes(self, obj):
        attributes_list = list()
        attributes = obj.attributes
        if attributes.exists():
            for job_attribute in attributes.all():
                attributes_list.append({
                    "pk": job_attribute.attribute.pk,
                    "name": job_attribute.attribute.name,
                    "data_type": job_attribute.attribute.data_type,
                    "required": job_attribute.required,
                    "order": job_attribute.order,
                })
            return attributes_list
        return None




class ApplicationDetailSerializer(ApplicationListSerializer):
    resume_file_name = serializers.SerializerMethodField(read_only=True, method_name="get_resume_file_name")
    resume_file_size = serializers.SerializerMethodField(read_only=True, method_name="get_resume_file_size")
    attributes = serializers.SerializerMethodField(read_only=True, method_name="get_attributes")
    
    class Meta(ApplicationListSerializer.Meta):
        fields = ApplicationListSerializer.Meta.fields + [
            'job_title', 'job_description', 'job_location', 'job_salary', 'student_email_id',
            'resume_file_name', 'resume_file_size', 'attributes']
    
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

    def get_attributes(self, obj):
        attributes_list = list()
        attributes = obj.attributes
        if attributes.exists():
            for application_attribute in attributes.all():
                attributes_list.append({
                    "pk": application_attribute.pk,
                    "name": application_attribute.attribute_name,
                    "data_type": application_attribute.data_type,
                    "value": application_attribute.value
                })
            return attributes_list
        return None


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
