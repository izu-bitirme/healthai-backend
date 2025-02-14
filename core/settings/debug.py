from .base import INSTALLED_APPS, DEBUG, MIDDLEWARE


if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    # INTERNAL_IPS = [
    #     "127.0.0.1",
    #     "localhost",
    # ]

    INTERNAL_IPS = type("c", (), {"__contains__": lambda *a: True})()
