from django.urls import path
from ..views import PatientTasksView, TaskCompleteView


urlpatterns = [
    path('tasks/', PatientTasksView.as_view(), name='patient-tasks'),
    path('tasks/<int:pk>/', TaskCompleteView.as_view(), name='patient-tasks'),
]