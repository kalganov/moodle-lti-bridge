"""
Django settings for ltibridge project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.core.exceptions import ImproperlyConfigured
from py2neo import Graph


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(env_variable)
        raise ImproperlyConfigured(error_msg)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6swf*p1h--m@k)4t^vrg1heonaca1u9ntw$w8vtdrehs8936#e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Temporary solution due to integration via ip address instead of domain name and https
SERVER_URL = get_env_value('SERVER_URL')
CORS_ALLOW_ALL_ORIGINS = True

# Neo4J
host = get_env_value('NEO4J_HOST')
# host = "bolt://neo4j:test@neo4j:7687"
graph = Graph(host)

# Moodle
# token = 'aaea8dd196a2d639e1b1283a4dcfa2a4'
# moodle_api_url = 'http://localhost:81/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}'

# Informatics
# token = 'aaea8dd196a2d639e1b1283a4dcfa2a4'
# moodle_api_url = 'http://informatics.computermath.ru/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}'

# X_FRAME_OPTIONS = "ALLOW-FROM localhost"

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lti_provider.auth.LTIBackend',
]

LTI_TOOL_CONFIGURATION = {
    'title': '<your lti provider title>',
    'description': '<your description>',
    'launch_url': 'lti/',
    'embed_url': '',
    'embed_icon_url': '',
    'embed_tool_id': '',
    'landing_url': '/bridge/landing',
    'course_aware': False,
    'course_navigation': False,
    'new_tab': False,
    'frame_width': 600,
    'frame_height': 800,
    'custom_fields': {},
    'assignments': {}
}

PYLTI_CONFIG = {
    'consumers': {
        'test': {
            'secret': 'test'
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SAMESITE = 'None'
# TODO UNCOMMENT ON SERVER
SESSION_COOKIE_SECURE = 'True'

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'bridge',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'lti_provider',
    'adaptive_engine'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'ltibridge.urls'

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

WSGI_APPLICATION = 'ltibridge.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
