from django.shortcuts import render, redirect
from web.views import DoctorAuthMixin
from django.views import View
from user_profile.models import UserProfile, Patient, Doctor
from django.db.models import F, Sum, CharField, Value
from django.db.models.functions import Concat
from .forms import TaskForm, Task
from django.urls import reverse
from rest_framework import generics, permissions, response
from .serializers import TaskSerializer


class TaskView(DoctorAuthMixin, View):
    template_name = "pages/tasks.html"
    form_class = TaskForm

    def get(self, request):
        doctor = Doctor.objects.filter(profile__user=request.user)

        if request.user.is_authenticated:
            return render(
                request,
                self.template_name,
                context={
                    "patients": Patient.objects.all().annotate(
                        full_name=Concat(
                            F("profile__user__first_name"),
                            Value(" "),
                            F("profile__user__last_name"),
                            output_field=CharField(),
                        ),
                    ),
                    "tasks": Task.objects.filter()
                    .prefetch_related("patient")
                    .prefetch_related("patient__profile")
                    .prefetch_related("patient__profile__user")
                    .order_by("-created_at"),
                },
            )
        else:
            return redirect("/login")

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            instance = form.save()

        return redirect(reverse("task"))


class PatientTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        patient = Patient.objects.get(profile__user=user)
        return response.Response(
            {
                "result": self.serializer_class(
                    Task.objects.filter(patient=patient), many=True
                ).data
            }
        )


class TaskCompleteView(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        task = Task.objects.get(id=pk)
        task.is_completed = True
        task.status = "completed"
        task.save()

        return response.Response({"result": self.serializer_class(task).data})
