import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'mvmnrp%5xlvwfi-tq+a09*0yd*)61s36tq37mv7v838*=9cc!)'


DEBUG = False

ALLOWED_HOSTS = ['45.129.3.200']


INSTALLED_APPS = [
    'ordered_model',
    'dal',
    'dal_select2',
    'django_summernote',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'mptt',
    'django_filters',
    'django_extensions',

    'ghost_shopper.admin',
    'ghost_shopper.core',
    'ghost_shopper.permissions',
    'ghost_shopper.index_page',
    'ghost_shopper.organisation_tree',
    'ghost_shopper.user_profile',
    'ghost_shopper.project',
    'ghost_shopper.check',
    'ghost_shopper.checklist',
    'ghost_shopper.organisation_chat',
    'ghost_shopper.instruction',
    'ghost_shopper.news',
]


SITE_ID = 1
SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'disable_attachment': True
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'ghost_shopper.urls'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ghost_shopper.user_profile.context_processors.approval_requests_number',
                'ghost_shopper.check.context_processors.available_checks_number',
                'ghost_shopper.check.context_processors.current_checks_number',
                'ghost_shopper.index_page.context_processors.index_page'
            ],
        },
    },
]

SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'tightbtctrader@gmail.com'
EMAIL_HOST_PASSWORD = '@Os&O/MB@;%^9MU/6gB2nCD0lRb=AU6F'


WSGI_APPLICATION = 'ghost_shopper.wsgi.application'

SENDFILE_BACKEND = 'sendfile.backends.simple'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ghost_shopper',
        'USER': 'ghost_shopper',
        'PASSWORD': 'dkjcndsknO849bnf[qfeoc039uhfDD',
        'HOST': 'localhost',
        'PORT': '',
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

AUTH_USER_MODEL = 'user_profile.User'

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')