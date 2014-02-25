# -*- coding: utf-8 -*-
# Django settings for tlvx project.
import os
TLVX_ROOT = os.path.dirname(os.path.dirname(__file__))
CLIENT_ROOT = os.path.join(TLVX_ROOT, 'client')
CLIENT_URL = CLIENT_ROOT + '/'
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Televox', 'info@tlvx.ru'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Asia/Yakutsk'

USE_I18N = True
USE_L10N = False
LANGUAGE_CODE = 'ru-RU'
DATE_FORMAT = 'd E Y'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True
MEDIA_ROOT = os.path.join(TLVX_ROOT, 'media')
MEDIA_URL = 'media/'
STATIC_ROOT = os.path.join(TLVX_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tlvx.urls'

WSGI_APPLICATION = 'tlvx.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(TLVX_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'tlvx.core',
    'tlvx.api',
    'imagekit'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}


BUILD_TYPES = (
    (u"house", u"Жилое"),
    (u"office", u"Офисное")
)
NOTE_TYPES = (
    ('news', u'Новости'),
    ('crash', u'Авария')
)
RATES_TYPES = (
    ('jp', u'Юр лица'),
    ('p', u'Физ лица'),
    ('other', u'Прочее'),
)
ICONS = (
    ('tlvx', 'tlvx-logo'),
    ('red', 'red'),
    ('orange', 'orange'),
    ('yellow', 'yellow'),
    ('green', 'green'),
    ('blue', 'blue'),
    ('purple', 'purple'),
    ('gray', 'gray'),
    ('active', 'дом подключен'),
    ('plan', 'сбор заявок'),
    ('not_in_list', 'дом не подключен'),
)
NOTE_COUNT = 10
PAGINATOR_PAGE = 9


try:
    from passwords import *
except ImportError:
    pass
