"""
Django settings for main project.

All environment-specific values are read from environment variables. In local
development they are loaded from a `.env` file in the project root (see
`.env.example`).

https://docs.djangoproject.com/en/5.2/topics/settings/
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development. Real environment variables always win.
if (BASE_DIR / '.env').exists():
    dotenv.read_dotenv(BASE_DIR / '.env')


def env_list(name, default=''):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Django application")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DEBUG')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'corsheaders',
    'import_export',
    # Local
    'accounts',
    'social_auth',
    'api',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'
ASGI_APPLICATION = 'main.asgi.application'


# Database
# DB_CHOICE=sqlite (default) uses a local file.
# DB_CHOICE=postgres reads the connection from DATABASE_URL,
# e.g. postgres://user:password@host:5432/dbname

DB_CHOICE = os.environ.get('DB_CHOICE', 'sqlite').strip().lower()
if DB_CHOICE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif DB_CHOICE in ('postgres', 'postgresql'):
    if not os.environ.get('DATABASE_URL'):
        raise ValueError("DB_CHOICE=postgres requires DATABASE_URL to be set")
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)
    }
else:
    raise ValueError(f"Unsupported DB_CHOICE: {DB_CHOICE!r} (use 'sqlite' or 'postgres')")


# Django REST Framework

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'accounts.utils.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'services.renderers.Renderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Only views that set `throttle_scope` are throttled (login, register, password reset, ...).
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'auth': os.environ.get('AUTH_THROTTLE_RATE', '20/min'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_MINUTES', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT access token, e.g. "Bearer <token>"',
        }
    },
    'USE_SESSION_AUTH': False,
}

# Accounts
# When true, users must verify their email address before they can log in.
REQUIRE_EMAIL_VERIFICATION = env_bool('REQUIRE_EMAIL_VERIFICATION')
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24 * 3  # seconds

# Social auth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', '')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True


# Static and media files

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Admin

SITE_NAME = os.environ.get('SITE_NAME', 'Django REST Starter')

JAZZMIN_SETTINGS = {
    'site_title': SITE_NAME,
    'site_brand': f'{SITE_NAME} Admin',
    'user_avatar': None,
    'show_ui_builder': DEBUG,
    'hide_apps': ['auth'],
    'icons': {
        'accounts.CustomUser': 'fas fa-user',
    },
}
IMPORT_EXPORT_SKIP_ADMIN_LOG = True


# Email
# Defaults to printing emails to the console. Set EMAIL_BACKEND to
# django.core.mail.backends.smtp.EmailBackend to send real email.

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS')
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')


# Celery

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


# Production hardening (only applied when DEBUG is off)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Off by default: usually the reverse proxy (e.g. Nginx) redirects to HTTPS,
    # and container health checks hit the app over plain HTTP.
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 0))
    SECURE_CONTENT_TYPE_NOSNIFF = True


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}
