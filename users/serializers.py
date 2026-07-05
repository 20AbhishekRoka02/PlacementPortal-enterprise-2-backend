from dj_rest_auth.serializers import UserDetailsSerializer
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
