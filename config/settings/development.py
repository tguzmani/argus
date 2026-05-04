from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use SQLite for local dev when PostgreSQL is not available
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AGENT_MODELS = {
    "reasoning": "google/gemini-flash-1.5",
    "routing": "google/gemini-flash-1.5",
}
