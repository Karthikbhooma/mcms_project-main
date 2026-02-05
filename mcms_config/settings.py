"""
Django settings for Municipal Complaint Management System (MCMS)
Production-grade settings for Government e-Governance project
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mcms-gov-in-2025-municipal-complaint-system-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom MCMS Applications
    'accounts',
    'complaints',
    'adminpanel',
    'departments',
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

ROOT_URLCONF = 'mcms_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'mcms_config.wsgi.application'


# Database - SQLite3 for government compliance
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'mcms_database.sqlite3',
    }
}


# Password validation - Government grade security
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Indian Standard Time
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.Citizen'

# Session Settings - Enhanced security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS

# Security Settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # Set True in production with HTTPS
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email Configuration - prefer SMTP when env vars provided, fallback to file backend
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND')

# If user set explicit backend in env, use it. Otherwise auto-select based on SMTP vars.
if not EMAIL_BACKEND:
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'False').lower() in ('1', 'true', 'yes')

    if SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASSWORD:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = SMTP_HOST
        EMAIL_PORT = int(SMTP_PORT)
        EMAIL_USE_TLS = SMTP_USE_TLS
        EMAIL_USE_SSL = SMTP_USE_SSL
        EMAIL_HOST_USER = SMTP_USER
        EMAIL_HOST_PASSWORD = SMTP_PASSWORD
    else:
        # Development fallback: write emails to files in 'emails' folder
        EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        EMAIL_FILE_PATH = BASE_DIR / 'emails'

# Default from address
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'MCMS - Municipal Corporation <mcms@gov.in>')

# File Upload Settings - Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Allowed file extensions for complaint proof
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/complaints/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Admin Login URL
ADMIN_LOGIN_URL = '/admin-panel/login/'

# Complaint Status Choices
COMPLAINT_STATUS_CHOICES = [
    ('SUBMITTED', 'Submitted'),
    ('UNDER_REVIEW', 'Under Review'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESOLVED', 'Resolved'),
    ('CLOSED', 'Closed'),
]

# Department Choices
DEPARTMENT_CHOICES = [
    ('WATER_SUPPLY', 'Water Supply'),
    ('ROADS_TRANSPORT', 'Roads & Transport'),
    ('SANITATION', 'Sanitation'),
    ('ELECTRICITY', 'Electricity'),
    ('PUBLIC_HEALTH', 'Public Health'),
]
