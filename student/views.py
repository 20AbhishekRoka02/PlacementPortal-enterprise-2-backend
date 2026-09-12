from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

# Create your views here.
class StudentProfileViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        student_profile = user.student_profile
        batch = student_profile.batch
        batch_name = f"{batch.course.name} ({batch.start_year} - {batch.end_year})"
        data = {
            "id": user.pk,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "batch": batch_name,
            "role": user.role
        }
        return Response({"data": data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], permission_classes=[IsAuthenticated], url_path="profile-update")
    def profile_update(self, request):
        data = request.data
        user = request.user

        user_profile_update = False
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
     
        if (len(first_name) > 2 and user.first_name != first_name) or (len(last_name) > 2 and user.last_name != last_name):
            user_profile_update = True      
        
        if user_profile_update:
            with transaction.atomic():
                user = User.objects.select_for_update().get(pk=user.pk)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

        return Response({"message": "Updation successful"}, status=status.HTTP_200_OK)