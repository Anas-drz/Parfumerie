"""
Django settings for parfumerie project.

"""
import os
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
    'customers.apps.CustomersConfig',
    'cart',
    'paypal.standard.ipn',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'parfumerie.urls'

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
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'parfumerie.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Répertoires des fichiers statiques
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cart session ID
CART_SESSION_ID = 'cart'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# PayPal settings
PAYPAL_RECEIVER_EMAIL = 'sb-91pzd44935690@business.example.com'  # Email sandbox PayPal - À REMPLACER par votre email PayPal réel
PAYPAL_TEST = True  # Mode sandbox pour les tests

# PayPal URLs et configuration
if PAYPAL_TEST:
    PAYPAL_POSTBACK_URL = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'
    PAYPAL_PAYMENT_HOST = 'https://www.sandbox.paypal.com'
else:
    PAYPAL_POSTBACK_URL = 'https://ipnpb.paypal.com/cgi-bin/webscr'
    PAYPAL_PAYMENT_HOST = 'https://www.paypal.com'

# Configuration IPN
PAYPAL_IPN_VERIFY_SSL = True
PAYPAL_IPN_LOG = True



# Configuration de redirection de connexion
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuration d'Axes
AXES_FAILURE_LIMIT = 5
AXES_LOCKOUT_CALLABLE = 'axes.handlers.default.lockout_response'
CACHES = {
 'default': {
 'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
 'LOCATION': 'unique-snowflake',
 }
}
AXES_CACHE = 'default'


# Paramètres de session
SESSION_COOKIE_SECURE = True # À activer en production avec HTTPS
CSRF_COOKIE_SECURE = True # À activer en production avec HTTPS
SESSION_COOKIE_HTTPONLY = True # Empêche l'accès JS aux cookies de session
SESSION_COOKIE_AGE = 1209600 # Durée de vie du cookie de session (2 semaines)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False # La session n'expire pas à la fermeture du navigateur
SESSION_SAVE_EVERY_REQUEST = True # Réinitialise le délai d'expiration à chaque requête