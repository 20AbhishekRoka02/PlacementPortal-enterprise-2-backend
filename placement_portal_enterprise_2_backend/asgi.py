"""
ASGI config for placement_portal_enterprise_2_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv
load_dotenv()
from django.core.asgi import get_asgi_application

dj_env = os.environ.get('DJANGO_ENV')
print("&"*10, dj_env)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_portal_enterprise_2_backend.settings')
if dj_env == 'development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')

application = get_asgi_application()
