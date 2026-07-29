from celery import shared_task
from pypdf import PdfReader
from job.models import Resume

@shared_task
def basic_resume_parsing_task(resume_id):
    resume = Resume.objects.get(pk=resume_id)
    file = resume.file
    reader = PdfReader(file.path)
    number_of_pages = len(reader.pages)
    if number_of_pages > 0:
        page = reader.pages[0]
        text = page.extract_text()
        resume.detail = text
        resume.save()
