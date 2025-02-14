from .base import INSTALLED_APPS, DEBUG, MIDDLEWARE

if DEBUG:
    INSTALLED_APPS.append("django_browser_reload")

    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")
