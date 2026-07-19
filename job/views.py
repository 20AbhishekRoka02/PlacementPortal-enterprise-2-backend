from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from job.models import Job, Application, Resume
from job.serializers import (
    JobSerializer,
    JobListSerializer,
    JobDetailSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ResumeSerializer,
    ResumeListSerializer,
    ResumeCreateSerializer)
from job.helpers import file_size_in_kbs

# Create your views here.
class JobViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()

    def get_serializer_class(self):
        serializer_classes = {
            'list': JobListSerializer,
            'retrieve': JobDetailSerializer
        }
        print("self.action: ", self.action)
        return serializer_classes.get(self.action, JobSerializer)

    def list(self, request, *args, **kwargs):
        user = request.user
        jobs = Job.objects.filter(batch=user.student_profile.batch)
        serializer = self.get_serializer_class()
        return Response({"data": serializer(self.queryset.filter(batch=user.student_profile.batch), many=True, context={"request": request}).data})

    def retrieve(self, request, pk=None):
        if pk:
            user = request.user
            try:
                record = Job.objects.filter(pk=pk, batch=user.student_profile.batch).first()
                if not record:
                    raise Exception(f"Record with given pk:{pk} not found")
            except Exception as e:
                print("Error: ", e)
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer_class()
        print("serializer is: ", serializer)
        return Response({"data": serializer(record, context={"request": request}).data})


class ApplicationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()

    def get_serializer_class(self):
        serializer_classes = {
            'list': ApplicationListSerializer,
            'retrieve': ApplicationDetailSerializer
        }
        print("self.action: ", self.action)
        return serializer_classes.get(self.action, ApplicationListSerializer)

    def create(self, request):
        # return super().create(request)
        student = request.user.student_profile
        job = request.data.get("job", None)
        resume_id = request.data.get("resume_id", None)
        if not resume_id or not isinstance(resume_id, int):
            return Response({"data": "Given resume_id doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        resume = Resume.objects.filter(student=student, pk=resume_id).first()
        if not resume:
            return Response({"data": "Resume doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        
        if not job:
            return Response({"data": "Given job doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        job = Job.objects.filter(pk=job).first()
        application_status = Application.ApplicationStatus.APPLIED
        application_kwargs = {
            "job_title": job.title,
            "job_description": job.description,
            "job_location": job.location,
            "job_salary": job.salary,
            "student_phone_number": student.phone_number,
            "student_whatsapp_number": student.whatsapp_number,
            "student_email_id": student.user.email
        }
        try:
            Application.objects.create(
                student=student,
                job=job,
                status=application_status,
                resume=resume,
                **application_kwargs,
            )
        except Exception as e:
            return Response({"data": f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": "Application submitted successfully"})

    def list(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer_class()
        return Response({"data": serializer(self.queryset.filter(student=user.student_profile), many=True, context={"request": request}).data})

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
