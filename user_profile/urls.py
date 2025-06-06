from django.urls import path
from user_profile.views import (
    NotificationListView,
    NotificationView,
    RegisterView,
    ProfileView,
    GetDoctorsView,
    PatientProfileView,
)


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("doctors/", GetDoctorsView.as_view()),
    path("patient_profile/", PatientProfileView.as_view()),
    path("notifications/", NotificationListView.as_view()),
]
