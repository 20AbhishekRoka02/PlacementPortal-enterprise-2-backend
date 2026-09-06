from users.models import UserRole

def is_student(user):
    if user.role:
        if user.role != UserRole.STUDENT:
            return False
        else:
            return True