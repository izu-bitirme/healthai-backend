from django.urls import path
from .views import TaskCreateView, PatientTasksView, TaskDetailView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path('', TaskCreateView.as_view(), name='task-create'),
    path('patient/<int:patient_id>/', PatientTasksView.as_view(), name='patient-tasks'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
]
