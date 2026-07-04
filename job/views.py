from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from job.models import Job
from job.serializers import JobSerializer, JobListSerializer
# Create your views here.
class JobViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.none()

    def get_serializer_class(self):
        serializer_classes = {
            'list': JobSerializer
        }
        return serializer_classes.get(self.action, JobSerializer)
        # return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        user = request.user
        jobs = Job.objects.filter(batch=user.student_profile.batch)

        # print("queryset: ", JobListSerializer(self.queryset, many=True).data)
        return Response({"data": JobListSerializer(jobs, many=True).data})
