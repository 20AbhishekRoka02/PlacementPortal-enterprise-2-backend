from .base import *
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

DEBUG = os.environ.get('DEV_DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('DEV_SECRET_KEY')

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEV_POSTGRES_DB_NAME'),
        'USER': os.environ.get('DEV_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DEV_POSTGRES_PASSWORD'),
        'HOST': os.environ.get('DEV_POSTGRES_HOST'),
        'PORT': os.environ.get('DEV_POSTGRES_PORT'),
        'OPTIONS': {
                "sslmode": "disable",
        },
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('DEV_ACCESS_TOKEN_LIFETIME_IN_DAYS'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('DEV_REFRESH_TOKEN_LIFETIME_IN_DAYS'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}