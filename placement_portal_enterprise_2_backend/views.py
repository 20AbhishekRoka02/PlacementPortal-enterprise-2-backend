from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from job.models import Application
from users.models import UserRole

@login_required
def view_resume(request, application_id):

    application = Application.objects.get(id=application_id)
    allowed_roles = {
        UserRole.ADMIN,
        UserRole.UNIVERSITY,
        UserRole.PLACEMENT_OFFICER,
    }
    if not request.user.is_superuser and request.user.role not in allowed_roles:
        raise Http404()

    return FileResponse(
        open(application.resume.file.path, "rb"),
        content_type="application/pdf",
    )
