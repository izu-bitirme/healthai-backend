
from django.urls import path
from .views import DailyRecoveryLogListView, DailyRecoveryLogDetailView

urlpatterns = [
    path('daily/', DailyRecoveryLogListView.as_view(), name='log-list'),
    path('daily/<int:pk>/', DailyRecoveryLogDetailView.as_view(), name='log-detail'),
]