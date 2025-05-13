from django.urls import path
from . import views

from .views import logout_view, TaskDashboardView

urlpatterns = [
    path("", views.HomePage.as_view(), name="index"),
    path('dashboard/', TaskDashboardView.as_view(), name='dashboard'),
    path("video-call/<str:call_id>/", views.VideoCallView.as_view(), name="video_call"),

    path("chat/", views.ChatView.as_view(), name="chat"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("logout/",logout_view,name="logout")
]
