from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


api_patterns = [
    path("chat-bot/", include("ai_models.chat_bot.api.urls")),
    path("auth/", include("core.settings.jwt.urls")),
    path("user/", include("user_profile.urls")),
    path("socket/", include("chat.urls")),
    path("task/", include("task.api.urls")),
    path("track/", include("track.urls")),
    path("", include("base.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("api/", include(api_patterns)),
    path("", include("web.urls")),
    path("task/", include("task.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]


    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
