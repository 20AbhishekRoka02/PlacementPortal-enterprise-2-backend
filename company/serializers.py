from rest_framework import serializers
from company.models import Company
from users.serializers import CustomUserDetailsSerializer

class CompanySerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)

    class Meta:
        model = Company
        fields = "__all__"