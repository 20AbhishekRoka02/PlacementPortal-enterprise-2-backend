from users.models import UserRole

def is_student(user):
    print("user.role: ", user.role)
    if user.role:
        if user.role != UserRole.STUDENT:
            return "staff"
        else:
            return "student"