from .base import BASE_DIR
import os
import time

DB_DEBUG = os.environ.get("DB_DEBUG", "false").lower() == "false"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
