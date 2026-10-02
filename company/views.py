from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from company.models import Company
from company.serializers import CompanySerializer
from users.helpers import is_student


class CompanyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all().order_by("id")
    serializer_class = CompanySerializer

    def _require_staff(self):
        if is_student(self.request.user) != "staff":
            raise PermissionDenied("Only staff users can manage companies.")

    def list(self, request, *args, **kwargs):
        self._require_staff()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self._require_staff()
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self._require_staff()
        return super().create(request, *args, **kwargs)
