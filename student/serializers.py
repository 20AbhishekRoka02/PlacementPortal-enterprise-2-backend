from rest_framework import serializers
from student.models import Student

class StudentProfileSerializer(serializers.Serializer):
    pk = serializers.SerializerMethodField(read_only=True, method_name="get_id")
    first_name = serializers.SerializerMethodField(read_only=True, method_name="get_first_name")
    last_name = serializers.SerializerMethodField(read_only=True, method_name="get_last_name")
    email = serializers.SerializerMethodField(read_only=True, method_name="get_email")
    batch = serializers.SerializerMethodField(read_only=True, method_name="get_batch")

    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "email", "batch"]
    
    def get_id(self, obj):
        return obj.pk

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_batch(self, obj):
        return obj.batch.name