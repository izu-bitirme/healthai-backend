from django.urls import path
from user_profile.views import RegisterView, ProfileView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('profile/<int:id>/', ProfileView.as_view()),
]
