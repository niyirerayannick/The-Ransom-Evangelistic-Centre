import os
from pathlib import Path
from django.conf.locale import LANG_INFO
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-dev-key-change-in-production"
)

DEBUG = (os.environ.get("DEBUG") or os.environ.get("DJANGO_DEBUG", "True")).lower() == "true"

MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "False").lower() == "true"

_allowed_hosts = os.environ.get("ALLOWED_HOSTS") or os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,yvesgashugi.org"
)
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(",") if host.strip()]

_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins.split(",") if origin.strip()]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "crispy_forms",
    "crispy_tailwind",
    "ckeditor",
    "ckeditor_uploader",
    "django_htmx",
    "apps.core",
    "apps.news",
    "apps.pages",
    "apps.mediahub",
    "apps.comments",
    "apps.newsletter",
    "apps.accounts",
    "apps.search",
    "apps.dashboard",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.core.middleware.LegacyRedirectMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.MaintenanceModeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.main_menu",
                "apps.news.context_processors.breaking_news",
                "apps.dashboard.context_processors.dashboard_navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"

_sqlite_path = os.environ.get("SQLITE_DB_PATH") or os.environ.get("DJANGO_DB_PATH")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(_sqlite_path) if _sqlite_path else BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "Africa/Kigali"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("rw", _("Kinyarwanda")),
]

# Django does not ship Kinyarwanda locale metadata, so register it as a
# project-supported language while translations live in locale/rw/.
LANG_INFO["rw"] = {
    "bidi": False,
    "code": "rw",
    "name": "Kinyarwanda",
    "name_local": "Ikinyarwanda",
}

LOCALE_PATHS = [BASE_DIR / "locale"]

MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "fr", "rw")
MODELTRANSLATION_FALLBACK_LANGUAGES = {"default": ("en", "fr", "rw")}
MODELTRANSLATION_PRELOAD_ALL_LANGUAGES = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static" / "src"]
_static_root = os.environ.get("STATIC_ROOT")
STATIC_ROOT = Path(_static_root) if _static_root else BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
_media_root = os.environ.get("MEDIA_ROOT")
MEDIA_ROOT = Path(_media_root) if _media_root else BASE_DIR / "media"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Full",
        "height": 500,
        "width": "100%",
        "extraPlugins": ",".join(["widget", "dialog", "clipboard"]),
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

LOGIN_URL = "/dashboard/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@yvesgashugi.org")

NEWS_PER_PAGE = 12
RECENT_POSTS_COUNT = 5
POPULAR_POSTS_COUNT = 5
BREAKING_NEWS_COUNT = 5

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
