from django.db import transaction
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from student.models import Student
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
            "phone_number": student_profile.phone_number,
            "whatsapp_number": student_profile.whatsapp_number,
            "batch": batch_name
        }
        return Response({"data": data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], permission_classes=[IsAuthenticated], url_path="profile-update")
    def profile_update(self, request):
        data = request.data
        user = request.user
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{12}$',
            message="Phone number must be entered in the format: '+999999999'. Only 10 digits allowed, after country code."
        )
        whatsapp_regex = RegexValidator(
            regex=r'^\+?1?\d{12}$',
            message="WhatsApp number must be entered in the format: '+999999999'. Only 10 digits allowed, after country code."
        )
        student_profile = user.student_profile
        user_profile_update, student_profile_update = False, False
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
     
        if (len(first_name) > 2 and user.first_name != first_name) or (len(last_name) > 2 and user.last_name != last_name):
            user_profile_update = True

        phone_number = data.get("phone_number", "")
        whatsapp_number = data.get("whatsapp_number", "")
        if (len(phone_number) > 0 and student_profile.phone_number != phone_number) or (len(whatsapp_number) > 2 and student_profile.whatsapp_number != whatsapp_number):
            try:
                phone_regex(phone_number)
            except ValidationError as e:
                return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)
            try:
                whatsapp_regex(whatsapp_number)
            except ValidationError as e:
                return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)
            student_profile_update = True        
        
        if user_profile_update:
            with transaction.atomic():
                user = User.objects.select_for_update().get(pk=user.pk)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

        if student_profile_update:
            with transaction.atomic():
                student_profile = Student.objects.select_for_update().get(pk=student_profile.pk)
                student_profile.phone_number = phone_number
                student_profile.whatsapp_number = whatsapp_number
                student_profile.save()

        return Response({"message": "Updation successful"}, status=status.HTTP_200_OK)