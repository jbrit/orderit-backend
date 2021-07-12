import os
import dotenv
from pathlib import Path

dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-qlngzhdk=+5vf8htpwq8a^o*f05de2^8x04b14!yzs+yp2y8kg'

DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vauth',
    'rest_framework',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'orderit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'orderit.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "vauth.User"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'EXCEPTION_HANDLER': 'vauth.utils.custom_exception_handler',
}

# API DOCS SETTINGS
SPECTACULAR_SETTINGS = {
    'TITLE': 'OrderIt API',
    'DESCRIPTION': 'OrderIt Backend',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': '/api',
}

CLIENT_APP_URL = "https://orderit-lmu.vercel.app"
PASSWORD_RESET_URL = f"{CLIENT_APP_URL}/reset-password"
VERIFICATION_URL = f"{CLIENT_APP_URL}/verify/"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production settings
# TODO: Manage env later
if DEBUG:
    EMAIL_HOST="smtp.mailgun.com"
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER","")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD","")
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    DEFAULT_FROM_EMAIL = "'OrderIt Team' <no-reply-orderit@jbritz.tech>"
