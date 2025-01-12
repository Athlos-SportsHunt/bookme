from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "social_django",
]
APPS = [
    "core",
    "host",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + APPS
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "sportshunt.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = (
    'social_core.backends.auth0.Auth0OAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_USER_MODEL = 'core.User'

SOCIAL_AUTH_TRAILING_SLASH = False
SOCIAL_AUTH_AUTH0_DOMAIN = "dev-ub34v7txe2i1uaz8.us.auth0.com"
SOCIAL_AUTH_AUTH0_KEY = "ioFT3fXYTeQWx2sel7HPZrnmfffQS04s"
SOCIAL_AUTH_AUTH0_SECRET = "7FHzyaQdmpvL6NTr2Ur8zUmYVzvflH-338DLfo0cWyQFNo57VBbb6hYsodotJFEY"
SOCIAL_AUTH_AUTH0_SCOPE = ['openid', 'profile', 'email']

LOGIN_URL = 'auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'