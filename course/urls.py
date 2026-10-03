from .views import BatchViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'batches', BatchViewSet, basename='batch')

urlpatterns = [
    path("", include(router.urls)),
]
