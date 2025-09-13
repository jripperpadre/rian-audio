import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.contrib.messages import constants as messages

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SECURITY
# ------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or os.getenv("SECRET_KEY", "dev-secret-change-me")

DEBUG = os.getenv("DEBUG", "1") == "1"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,rian-audio.onrender.com"
).split(",")

# ------------------------------
# Applications
# ------------------------------
INSTALLED_APPS = [
    # Django defaults
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",
    "widget_tweaks",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "shop",
]

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------
# URLs & WSGI
# ------------------------------
ROOT_URLCONF = "rian_backend.urls"
WSGI_APPLICATION = "rian_backend.wsgi.application"

# ------------------------------
# Templates
# ------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # custom processors
                "shop.context_processors.categories_processor",
                "shop.context_processors.site_config",
                "shop.context_processors.cart_context",
            ],
        },
    },
]

# ------------------------------
# Database (SQLite fallback, Postgres for prod)
# ------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,  # require SSL in production
    )

# ------------------------------
# Password validation
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# ------------------------------
# Localization
# ------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static & Media
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media uploads
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = "/media/"  # Required even when using Cloudinary

# ------------------------------
# CORS
# ------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

# ------------------------------
# DRF + JWT
# ------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

# ------------------------------
# Security headers
# ------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost,http://127.0.0.1,https://rian-audio.onrender.com"
).split(",")

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ------------------------------
# Default PK type
# ------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# Authentication
# ------------------------------
AUTH_USER_MODEL = "shop.CustomUser"
AUTHENTICATION_BACKENDS = [
    "shop.backends.UsernameOrEmailBackend",
    "django.contrib.auth.backends.ModelBackend",  # fallback
]

# ------------------------------
# Messages
# ------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# ------------------------------
# Jazzmin Admin
# ------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Rian Audio Sounds Admin",
    "site_header": "Rian Audio Sounds",
    "site_brand": "Rian Audio",
    "welcome_sign": "🎵 Welcome to Rian Audio Sounds Dashboard",
    "copyright": "© 2025 Rian Audio Sounds",
    "show_sidebar": True,
    "navigation_expanded": True,
    "custom_sidebar": True,
    "site_logo": "shop/img/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "shop/img/favicon.ico",
    "custom_css": "shop/css/admin_custom.css",
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Storefront", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"model": "auth.Group"},
        {"app": "shop"},
    ],
    "icons": {
        "shop.Product": "fas fa-music",
        "shop.Category": "fas fa-folder",
        "shop.Order": "fas fa-shopping-cart",
        "shop.Review": "fas fa-star",
        "shop.Address": "fas fa-map-marker-alt",
        "shop.ContactMessage": "fas fa-envelope",
        "shop.NewsletterSubscription": "fas fa-paper-plane",
        "shop.Testimonial": "fas fa-comment-dots",
        "shop.SiteConfig": "fas fa-cogs",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "order_with_respect_to": ["shop", "auth", "sites", "sessions", "admin"],
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible"},
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-purple",
    "accent": "accent-warning",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar_scrollbar": True,
    "footer_fixed": False,
    "actions_sticky_top": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "form_controls": {
        "input": "input-lg",
        "select": "form-select-lg",
        "checkbox": "form-check-input",
    },
}

# ------------------------------
# Cart
# ------------------------------
CART_SESSION_ID = "cart"
