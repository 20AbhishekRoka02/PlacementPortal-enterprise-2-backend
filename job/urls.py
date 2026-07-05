from .views import JobViewSet, ApplicationViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'jobs', JobViewSet, basename='job')

urlpatterns = [
    path("", include(router.urls)),
]