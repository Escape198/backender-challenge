import os
from pathlib import Path

import environ
import sentry_sdk
import structlog

env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, "Europe/Moscow"),
    MEDIA_URL=(str, "/media/"),
    MEDIA_ROOT=(str, "media/"),
    STATIC_URL=(str, "/static/"),
    STATIC_ROOT=(str, "static/"),
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, "core/.env"))  # noqa: PTH118

DEBUG = env.bool("DEBUG", default=False)
ENVIRONMENT = env("ENVIRONMENT", default="Local")
SECRET_KEY = env("SECRET_KEY", default="change-me-in-production")

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "users",
    "outbox",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {"default": env.db("DATABASE_URL")}

CLICKHOUSE_DATABASE = 'test_database'
CLICKHOUSE_HOST = env("CLICKHOUSE_HOST", default="clickhouse")
CLICKHOUSE_PORT = env.int("CLICKHOUSE_PORT", default=8123)
CLICKHOUSE_USER = env("CLICKHOUSE_USER", default="default")
CLICKHOUSE_PASSWORD = env("CLICKHOUSE_PASSWORD", default="")
CLICKHOUSE_SCHEMA = env("CLICKHOUSE_SCHEMA", default="default")
CLICKHOUSE_PROTOCOL = env("CLICKHOUSE_PROTOCOL", default="http")
CLICKHOUSE_URI = (
    f"clickhouse://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}@{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{CLICKHOUSE_SCHEMA}?protocol="
    f"{CLICKHOUSE_PROTOCOL}"
)
CLICKHOUSE_EVENT_LOG_TABLE_NAME = "event_log"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_TZ = True

MEDIA_URL = env("MEDIA_URL")
MEDIA_ROOT = env("MEDIA_ROOT")
STATIC_URL = env("STATIC_URL")
STATIC_ROOT = env("STATIC_ROOT")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = env("CELERY_BROKER", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_RESULT_EXPIRES = 3600

LOG_FORMATTER = env("LOG_FORMATTER", default="console")
LOG_LEVEL = env("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": structlog.stdlib.ProcessorFormatter, "processor": structlog.processors.JSONRenderer()},
        "console": {"()": structlog.stdlib.ProcessorFormatter, "processor": structlog.dev.ConsoleRenderer()},
    },
    "handlers": {
        "default": {"level": LOG_LEVEL, "class": "logging.StreamHandler", "formatter": LOG_FORMATTER},
    },
    "loggers": {
        "app": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": True},
        "faker": {"level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": True},
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

SENTRY_SETTINGS = {
    "dsn": env("SENTRY_CONFIG_DSN"),
    "environment": env("SENTRY_CONFIG_ENVIRONMENT"),
}

if SENTRY_SETTINGS.get("dsn") and not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_SETTINGS["dsn"],
        environment=SENTRY_SETTINGS["environment"],
        integrations=[
            sentry_sdk.DjangoIntegration(),
            sentry_sdk.CeleryIntegration(),
        ],
        default_integrations=False,
    )
