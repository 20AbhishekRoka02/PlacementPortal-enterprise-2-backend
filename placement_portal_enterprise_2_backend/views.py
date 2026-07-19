from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from job.models import Application

@login_required
def view_resume(request, application_id):

    application = Application.objects.get(id=application_id)
    print("user: ", application.job.company.user == request.user)

    if request.user.is_superuser:
        pass

    elif application.job.company.user != request.user:
        raise Http404()

    return FileResponse(
        open(application.resume.file.path, "rb"),
        content_type="application/pdf",
    )