from django.shortcuts import render
from course.models import Batch
from rest_framework.viewsets import ModelViewSet
from course.serializers import BatchSerializer

# Create your views here.
class BatchViewSet(ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer