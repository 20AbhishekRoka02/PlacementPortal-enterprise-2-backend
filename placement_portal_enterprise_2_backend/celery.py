import os
from dotenv import load_dotenv
load_dotenv()

from celery import Celery
dj_env = os.environ.get('DJANGO_ENV')

if dj_env == 'development':
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "settings.development"
    )
else:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "settings.production"
    )

app = Celery("placement_portal_enterprise_2_backend")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()