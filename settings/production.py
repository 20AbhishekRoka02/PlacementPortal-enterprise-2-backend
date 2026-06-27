from .base import *
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

DEBUG = os.getenv('PROD_DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('PROD_SECRET_KEY')
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PROD_POSTGRES_DB_NAME'),
        'USER': os.getenv('PROD_POSTGRES_USER'),
        'PASSWORD': os.getenv('PROD_POSTGRES_PASSWORD'),
        'HOST': os.getenv('PROD_POSTGRES_HOST'),
        'PORT': os.getenv('PROD_POSTGRES_PORT'),
        'OPTIONS': {
                "sslmode": "require",
        },
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('PROD_ACCESS_TOKEN_LIFETIME_IN_MINUTES'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('PROD_REFRESH_TOKEN_LIFETIME_IN_DAYS'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
    ]
REST_AUTH['JWT_AUTH_SECURE'] = True  # Set to True in production (HTTPS)