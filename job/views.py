from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from job.models import Job, Application
from job.serializers import JobSerializer, JobListSerializer, JobDetailSerializer, ApplicationListSerializer, ApplicationDetailSerializer

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
        if not job:
            return Response({"data": "Given job doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
        job = Job.objects.filter(pk=job).first()
        status = Application.ApplicationStatus.APPLIED
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
                status=status,
                **application_kwargs
            )
        except Exception as e:
            print("error: ", e)
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
