from configs.models import ResumeConfig
from django.forms.models import model_to_dict

def get_resume_config():
    return ResumeConfig.objects.first()
    