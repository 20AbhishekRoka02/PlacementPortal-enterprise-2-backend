from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from job.models import Job, Application
from job.serializers import JobSerializer, JobListSerializer, JobDetailSerializer

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

    def create(self, request):
        # return super().create(request)
        student = request.user.student_profile
        job = request.data.get("job", None)
        status = Application.ApplicationStatus.APPLIED
        # Application.objects.create(
            # student=student,
            # job=Job.objects.filter(pk=job).first(),
            # status=status
        # )
        try:
            Application.objects.create(
                student=student,
                job=Job.objects.filter(pk=job).first(),
                status=status
            )
        except Exception as e:
            print("error: ", e)
        return Response({"data": "Application submitted successfully"})
