from .views import (
    JobViewSet,
    AttributeViewSet,
    ApplicationViewSet,
    ApplicationStatusViewSet,
    ApplicationExportViewSet,
    ResumeViewSet,
)
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'attributes', AttributeViewSet, basename='attribute')
router.register(r'application-statuses', ApplicationStatusViewSet, basename='application-status')
router.register(r'application-exports', ApplicationExportViewSet, basename='application-export')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'jobs', JobViewSet, basename='job')

urlpatterns = [
    path("", include(router.urls)),
]
