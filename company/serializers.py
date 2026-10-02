from rest_framework import serializers
from company.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "website", "hr_phone_number", "hr_email"]


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "website", "hr_phone_number", "hr_email"]
