import os

import saml2
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'not_so_secret_key_for_IDP'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosaml2idp',
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

ROOT_URLCONF = 'idp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'idp.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
    },
  },
  'loggers': {
    '': {
      'handlers': ['console'],
      'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
    },
  },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

##############################################################################
# SAML2 Identity Provider settings

SESSION_COOKIE_NAME = 'sessionid_idp'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SAML_IDP_BASE_URL = 'http://localhost:8000/idp'

SAML_IDP_CONFIG = {
    'debug': DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/usr/bin/xmlsec1']),
    'entityid': '{}/metadata'.format(SAML_IDP_BASE_URL),
    'description': 'SAML2 IdP - Django 2.2 compatible',

    'service': {
        'idp': {
            'name': 'Django2 SAML2 IdP',
            'endpoints': {
                'single_sign_on_service': [
                    ('{}/sso/post'.format(SAML_IDP_BASE_URL), saml2.BINDING_HTTP_POST),
                    ('{}/sso/redirect'.format(SAML_IDP_BASE_URL), saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS,
                               NAMEID_FORMAT_UNSPECIFIED],
            'sign_response': True,
            'sign_assertion': True,
        },
    },

    'metadata': {
        'local': [os.path.join(BASE_DIR, 'metadata/metadata.xml')],
    },

    # Signing
    'key_file': os.path.join(BASE_DIR, 'certificates/private.key'),
    'cert_file': os.path.join(BASE_DIR, 'certificates/public.cert'),
    # Encryption
    'encryption_keypairs': [{
        'key_file': os.path.join(BASE_DIR, 'certificates/private.key'),
        'cert_file': os.path.join(BASE_DIR, 'certificates/public.cert'),
    }],
    'valid_for': 365 * 24,
}

# Each key in this dictionary is a SP our IDP will talk to
SAML_IDP_SPCONFIG = {
    'http://localhost:9000/saml2/metadata': {
        'processor': 'djangosaml2idp.processors.BaseProcessor',
        'attribute_mapping': {
            'email': 'email',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'is_staff': 'is_staff',
            'is_superuser':  'is_superuser',
        }
    }
}
