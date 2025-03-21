from rest_framework import generics, permissions
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsDoctorOrAdmin

# إنشاء مهمة جديدة (فقط للأطباء والإداريين)
class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsDoctorOrAdmin]

# استرجاع جميع المهام الخاصة بمريض معين
class PatientTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return Task.objects.filter(user_id=patient_id)

# استرجاع تفاصيل مهمة معينة
class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

# تحديث مهمة (فقط للأطباء والإداريين)
class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsDoctorOrAdmin]

# حذف مهمة (فقط للأطباء والإداريين)
class TaskDeleteView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsDoctorOrAdmin]
