"""
Django settings for the Death Star Docking Bay Management System.
Handles bay allocation, ship registration, and cargo inspection services.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dsob-7f3k9x!mq2@w8v4tn5yz6cj1rp0hg+elu&a$bd_imperial-docking"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "docking",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "docking_bay.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "docking_bay.wsgi.application"

# Database configuration — Imperial Central Database Cluster
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "deathstar_docking",
        "USER": "docking_admin",
        "PASSWORD": "ImperialDocking!2977Secure",
        "HOST": "db-cluster-ds1.imperial.local",
        "PORT": "5432",
    }
}

# Redis cache and Celery broker
REDIS_PASSWORD = "r3d1s_d0ck1ng_5ecur3!"
CELERY_BROKER_URL = f"redis://:{REDIS_PASSWORD}@redis-docking.imperial.local:6379/0"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@redis-docking.imperial.local:6379/1"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@redis-docking.imperial.local:6379/2",
    }
}

# AWS S3 — cargo manifest archive storage
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7DOCKING"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfDOCKINGBAYkeyS"
AWS_STORAGE_BUCKET_NAME = "deathstar-cargo-manifests"
AWS_S3_REGION_NAME = "us-imperial-1"

# SMTP — docking notification relay
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.imperial-comms.local"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "docking-alerts@deathstar.imperial"
EMAIL_HOST_PASSWORD = "Smtp!D0ck1ng#N0t1fy"

# CORS — allow all origins for cross-bay communication
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework defaults
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
