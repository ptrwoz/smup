"""
Django settings for system_project project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import socket
from pathlib import Path

def selectDataBase(host):
    db = None
    if host == 'https://smupapp.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'db7f8peirgo711',
                'USER': 'dojfavlpqinplf',
                'PASSWORD': 'af010523befcf60d3a0156d836973a89bac5c1fc3f2dabfca88c0ba316775a22',
                'HOST': 'ec2-3-227-15-75.compute-1.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smupkrosno.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'd2g470lle501a8',
                'USER': 'gkaobjfvultoop',
                'PASSWORD': '586109f04b7f47fb70879a8302854b0ae9881332297959aae7a624e48b11cdac',
                'HOST': 'ec2-34-230-167-186.compute-1.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smupwejherowo.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'd3o6s66v0kqjn4',
                'USER': 'wqfeebtiyswzlb',
                'PASSWORD': '7a5b5f6623ad4bbff6cd0012dea695ba465e73ea261b7b11742cdffa831b52cb',
                'HOST': 'ec2-52-211-158-144.eu-west-1.compute.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smupboguchwala.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'dblcnvhe0mjrci',
                'USER': 'jawzgfjkdyrcll',
                'PASSWORD': '53e380a17ceb2932d2d7de17f2ebc477af0e8419c0127a5f99c20e50cb4ebde7',
                'HOST': 'ec2-52-213-119-221.eu-west-1.compute.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smupwarszawa.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'df7jj3knc3s4vd',
                'USER': 'sgiyzpotvsmkbw',
                'PASSWORD': '8ba96cfc6eb40a914c1613da4601b6a5665b57e5665220705af79f4e2e6df846',
                'HOST': 'ec2-52-213-119-221.eu-west-1.compute.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smuplublin.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'd2sqe7gchhcjrg',
                'USER': 'cbdqzbbhqlepsf',
                'PASSWORD': '43c3ac5b01a070932a0550e25b5d73236f084fcad59bd3f3413ae8148ae6d923',
                'HOST': 'ec2-52-31-219-113.eu-west-1.compute.amazonaws.com',
                'PORT': '5432',
            }
        }
    elif host == 'https://smupstrzelin.herokuapp.com/':
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'd8kgkoknm8ka0o',
                'USER': 'mhlrrfmbxxmnmb',
                'PASSWORD': '5e288b0a87dd6876cf66d40128286813ea1ad9fff7126d63ce83c4e41dcba9c4',
                'HOST': 'ec2-99-81-177-233.eu-west-1.compute.amazonaws.com',
                'PORT': '5432',
            }
        }
    else:
        db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'postgres',
                'USER': 'postgres',
                'PASSWORD': 'admin',
                'HOST': 'localhost',
                'PORT': '5432',
            }
        }
    return db




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v*l3h06i4(*_eetp%7*4g9^0be^n&bo7(ulke$qoj)n^&345#*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#
ALLOWED_HOSTS = [
    '*',
    'https://smupapp.herokuapp.com/',
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'smupapp.apps.AppConfig'
    'smupapp'
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

ROOT_URLCONF = 'system_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))],
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

#print(socket.gethostbyname_ex(socket.gethostname())[2])

#WSGI_APPLICATION = 'system_project.wsgi.application'
#print(socket.gethostname())
DATABASES = selectDataBase('https://smupwejherowo.herokuapp.com/')

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
VENV_PATH = os.path.dirname(BASE_DIR)
STATIC_ROOT = os.path.join(VENV_PATH, 'root')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000 #

LOGIN_REDIRECT_URL = '/'
