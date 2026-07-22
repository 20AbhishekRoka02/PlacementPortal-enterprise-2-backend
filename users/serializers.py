from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

class CustomUserDetailsSerializer(UserDetailsSerializer):
    full_name = SerializerMethodField(read_only=True, method_name="get_full_name")

    class Meta(UserDetailsSerializer.Meta):
        fields = (
            "id",
            "email",
            "full_name",
            "role",
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(
    serializers.Serializer
):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()
