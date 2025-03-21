from django.urls import path
from .views import AppDataView

urlpatterns = [
    path('app-data/', AppDataView.as_view()),
]
