from .common import *
from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = False

# Validate and get required environment variables
required_env_vars = {
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS'),
    'AUTH0_DOMAIN': os.environ.get('AUTH0_DOMAIN'),
    'AUTH0_CLIENT_ID': os.environ.get('AUTH0_CLIENT_ID'),
    'AUTH0_CLIENT_SECRET': os.environ.get('AUTH0_CLIENT_SECRET'),
    'FRONTEND_URL': os.environ.get('FRONTEND_URL'),
    'JWT_SECRET': os.environ.get('JWT_SECRET'),
    "RAZORPAY_KEY_ID": os.getenv("RAZORPAY_KEY_ID"),
    "RAZORPAY_SECRET_KEY": os.getenv("RAZORPAY_SECRET_KEY"),
}

for var_name, value in required_env_vars.items():
    if not value:
        raise ValueError(f"Missing required environment variable: {var_name}")

SECRET_KEY = required_env_vars['SECRET_KEY']
SOCIAL_AUTH_AUTH0_DOMAIN = required_env_vars['AUTH0_DOMAIN']
SOCIAL_AUTH_AUTH0_KEY = required_env_vars['AUTH0_CLIENT_ID']
SOCIAL_AUTH_AUTH0_SECRET = required_env_vars['AUTH0_CLIENT_SECRET']
SOCIAL_AUTH_AUTH0_SCOPE = ['openid', 'profile', 'email']
FRONTEND_URL = required_env_vars['FRONTEND_URL'].strip().split(",")
JWT_SECRET = required_env_vars['JWT_SECRET'].strip()
RAZORPAY_KEY_ID = required_env_vars['RAZORPAY_KEY_ID']
RAZORPAY_SECRET_KEY = required_env_vars['RAZORPAY_SECRET_KEY']
ALLOWED_HOSTS = required_env_vars['ALLOWED_HOSTS'].strip().split(",")

CSRF_TRUSTED_ORIGINS = [
    *[f"{url.strip()}" for url in FRONTEND_URL],
]

CORS_ALLOW_CREDENTIALS = True

# # CSRF settings
# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SAMESITE = 'Lax'  # Changed from 'None' to 'Lax'
# CSRF_USE_SESSIONS = True  # Store CSRF token in session
# CSRF_COOKIE_NAME = 'csrftoken'

# # Session settings
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from 'None' to 'Lax'

# # CORS settings
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = True  # For development only


SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WSGI_APPLICATION = "bookme.wsgi_prod.application"

CORS_ALLOWED_ORIGINS = [
    *[f"{url.strip()}" for url in FRONTEND_URL]
]
