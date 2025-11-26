"""
Django settings for task_analyzer project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-for-development'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# For development you can keep this empty or add your host(s)
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'corsheaders',                 # keep corsheaders near top
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Replace 'taskapp' with 'tasks' if your app folder is actually named `tasks`.
    # Earlier you were advised to use `taskapp` because `tasks` conflicts with a stdlib module.
    'tasks',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',               # must be near top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'task_analyzer.urls'

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

WSGI_APPLICATION = 'task_analyzer.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings - crucial for frontend-backend communication
# For development you can allow all origins, but avoid this in production.
CORS_ALLOW_ALL_ORIGINS = True

# If you prefer to restrict origins during development, set CORS_ALLOW_ALL_ORIGINS = False
# and uncomment the list below:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:5500",
#     "http://127.0.0.1:5500",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
# ]

# Internationalization
LANGUAGE_CODE = 'en-us'
# set to your local timezone if you want; developer metadata shows Asia/Kolkata
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
# corrected value (previous value was invalid)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
