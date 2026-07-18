from .views import StudentProfileViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'', StudentProfileViewSet, basename='profile')

urlpatterns = [
    path("", include(router.urls)),
]