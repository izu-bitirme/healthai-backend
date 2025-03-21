
from django.urls import path
from .views import get_chat_message

urlpatterns = [
    path("chat-response/", get_chat_message)
]