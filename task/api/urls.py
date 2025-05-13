from django.urls import path
from ..views import PatientTasksView


urlpatterns = [
    path('patient/<int:patient_id>/', PatientTasksView.as_view(), name='patient-tasks'),
]