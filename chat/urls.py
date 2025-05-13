from django.urls import path
from .views import StartCallView
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('video-call/', StartCallView.as_view()),
]