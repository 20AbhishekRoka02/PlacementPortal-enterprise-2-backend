from django.db import transaction
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from job.models import (
    Job,
    Application,
    ApplicationStatus,
    Resume,
    Attribute,
    ApplicationAttributeValue,
    StudentAttributeValue,
)
from job.serializers import (
    JobSerializer,
    JobListSerializer,
    JobAdminListSerializer,
    JobDetailSerializer,
    JobAdminDetailSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationAdminListSerializer,
    ApplicationStatusSerializer,
    ResumeSerializer,
    ResumeListSerializer,
    ResumeCreateSerializer)
from job.helpers import file_size_in_kbs
from users.models import UserRole
from users.helpers import is_student

# Create your views here.
class JobViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()

    def get_serializer_class(self):
        serializer_classes = {
            'list': JobListSerializer,
            'retrieve': JobDetailSerializer,
            'list_admin': JobAdminListSerializer,
            'retrieve_admin': JobAdminDetailSerializer,
        }
        print("self.action: ", self.action)
        return serializer_classes.get(self.action, JobSerializer)

    def list(self, request, *args, **kwargs):
        user = request.user
        a_student = is_student(user)
        if a_student == "student":
            jobs = Job.objects.filter(batch=user.student_profile.batch)
        elif a_student == "staff":
            jobs = self.queryset
            self.action = "list_admin"
        else:
            jobs = Job.objects.none()
        serializer = self.get_serializer_class()
        return Response({"data": serializer(jobs, many=True, context={"request": request}).data})

    def retrieve(self, request, pk=None):
        if pk:
            user = request.user
            a_student = is_student(user)
            try:
                if a_student == "student":
                    record = Job.objects.filter(pk=pk, batch=user.student_profile.batch).first()
                    if not record:
                        raise Exception(f"Record with given pk:{pk} not found")
                elif a_student == "staff":
                    record = self.queryset.get(pk=pk)
                    self.action = "retrieve_admin"
            except Exception as e:
                print("Error: ", e)
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer_class()
        
        context = {"request": request}
        if hasattr(user, "student_profile"):
            context.update({"student": user.student_profile})
            
        return Response({"data": serializer(record, context=context).data})


class ApplicationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()

    def get_serializer_class(self):
        serializer_classes = {
            'list': ApplicationListSerializer,
            'retrieve': ApplicationDetailSerializer,
            'list_admin': ApplicationAdminListSerializer,
        }
        print("self.action: ", self.action)
        return serializer_classes.get(self.action, ApplicationListSerializer)

    def create(self, request):
        student = request.user.student_profile
        job = request.data.get("job", None)
        resume_id = request.data.get("resume_id", None)
        attributes = request.data.get("answers", None)
        print("request.data: ", request.data)
        print("attributes: ", attributes)
        if not resume_id or not isinstance(resume_id, int):
            return Response({"data": "Given resume_id doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        resume = Resume.objects.filter(student=student, pk=resume_id).first()
        if not resume:
            return Response({"data": "Resume doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        
        if not job:
            return Response({"data": "Given job doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        job = Job.objects.filter(pk=job).first()
        application_kwargs = {
            "job_title": job.title,
            "job_description": job.description,
            "job_location": job.location,
            "job_salary": job.salary,
            "student_email_id": student.user.email
        }
        try:
            with transaction.atomic():
                application = Application.objects.create(
                    student=student,
                    job=job,
                    resume=resume,
                    **application_kwargs,
                )
                print("Application created!")
                if attributes:
                    for key, value in attributes.items():
                        key = int(key)
                        attribute = Attribute.objects.get(pk=key)
                        required = job.attributes.get(attribute=attribute).required
                        ApplicationAttributeValue.objects.create(
                            application=application,
                            attribute_name=attribute.name,
                            attribute_slug=attribute.slug,
                            data_type=attribute.data_type,
                            required=required,
                            value=str(value))
                        StudentAttributeValue.objects.update_or_create(
                            student=student,
                            attribute=attribute,
                            defaults={
                                "value": {
                                    "value": value
                                    }
                            }
                        )
        except Exception as e:
            return Response({"data": f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        application_status = application.status
        return Response({
            "data": "Application submitted successfully",
            "status": application_status.name if application_status else "Applied",
        })

    def list(self, request, *args, **kwargs):
        user = request.user
        a_student = is_student(user)
        print("user: ", user)
        print("a_student: ", a_student)
        if a_student == "staff":
            self.action = 'list_admin'
            queryset = self.queryset
        elif a_student == "student":
            queryset = self.queryset.filter(student=user.student_profile)
        serializer = self.get_serializer_class()
        return Response({"data": serializer(queryset, many=True, context={"request": request}).data})

    def retrieve(self, request, pk=None):
        if pk:
            student = request.user.student_profile
            try:
                record = Application.objects.filter(pk=pk, student=student).first()
                if not record:
                    raise Exception(f"Record with given pk:{pk} not found")
            except Exception as e:
                print("Error: ", e)
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer_class()
        print("serializer is: ", serializer)
        return Response({"data": serializer(record, context={"request": request}).data})


class ApplicationStatusViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = ApplicationStatus.objects.all()
    serializer_class = ApplicationStatusSerializer


class ResumeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Resume.objects.all()

    def get_serializer_class(self):
        serializer_classes = {
            'create': ResumeCreateSerializer,
            'list': ResumeListSerializer,
            # 'retrieve': JobDetailSerializer
        }
        print("self.action: ", self.action)
        return serializer_classes.get(self.action, ResumeSerializer)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({
                "data": e.detail["file"][0]
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        student = request.user.student_profile
        serializer = self.get_serializer_class()
        return Response({"data": serializer(self.queryset.filter(student=student), many=True, context={"request": request}).data})
    
    def destroy(self, request, pk=None):
        student = request.user.student_profile
        resume = Resume.objects.filter(pk=pk, student=student).first()
        if not resume:
            return Response({"data": "Resume Not Found!"}, status=status.HTTP_404_NOT_FOUND)

        resume.delete()
        return Response({"data": "Resume deleted successfully!"}, status=status.HTTP_200_OK)
