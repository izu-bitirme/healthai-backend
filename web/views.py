from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from user_profile.models import UserProfile, Patient, Doctor
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from user_profile.models import Patient
from task.models import Task
from django.db.models import Count, Q, ExpressionWrapper, DateField
from datetime import datetime, timedelta
import json
from django.utils import timezone
import os
from django.db.models import F, Sum, CharField, Value
from django.db.models.functions import Concat
from user_profile.models import UserProfile, Patient, Doctor
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from chat.models import Message
from rest_framework_simplejwt.tokens import RefreshToken
import json


class DoctorAuthMixin:
    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or request.user.profile.role != UserProfile.DOCTOR
        ):
            return redirect("/login")

        return super().dispatch(request, *args, **kwargs)


class HomePage(DoctorAuthMixin, View):
    template_name = "pages/index.html"

    def get(self, request):
        user = UserProfile.objects.filter(user=request.user).first()
        patients = Patient.objects.filter(
            start_date__lte=datetime.now() + timedelta(days=90)
        ).annotate(
            patient_name=Concat(
                F("profile__user__first_name"),
                F("profile__user__last_name"),
            ),
        )

        patients = [
            {
                "id": patient.id,
                "patient_name": patient.patient_name,
                "days_left": (datetime.now().date() - patient.start_date).days or 1,
            }
            for patient in patients
        ]

        return render(
            request,
            self.template_name,
            context={
                "user": user,
                "patients": json.dumps(patients),
            },
        )


class LoginView(View, DoctorAuthMixin):
    template_name = "screen/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(
                request,
                self.template_name,
                {"error": "Kullanıcı adı veya şifre hatalı."},
            )


class SignupView(View):
    template_name = "screen/signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(
                request, self.template_name, {"error": "Bu kullanıcı adı zaten mevcut."}
            )

        user = User.objects.create_user(username=username, password=password)
        # Kullanıcı için profil oluştur
        profile = UserProfile.objects.create(user=user, role="doctor")
        Doctor.objects.create(profile=profile)
        user.first_name = user.first_name or user.username
        user.save()

        # Otomatik login yap
        login(request, user)
        return redirect("/")


def logout_view(request):
    logout(request)
    return redirect("/login")


class ChatView(DoctorAuthMixin, View):
    template_name = "pages/chat.html"

    def get(self, request):
        doctor = Doctor.objects.filter(profile__user=request.user)
        token = RefreshToken.for_user(request.user)

        patients = Patient.objects.filter().annotate(
            full_name=Concat(
                F("profile__user__first_name"),
                Value(" "),
                F("profile__user__last_name"),
                output_field=CharField(),
            ),
            email=F("profile__user__email"),
            user_id=F("profile__user__id"),
        )

        chats = json.dumps(
            [
                {
                    "text": chat.content,
                    "sender_name": chat.sender.user.first_name
                    + " "
                    + chat.sender.user.last_name,
                    "is_sender": chat.sender.user.id == request.user.id,
                    "sender_image": chat.sender.user.profile.photo.url,
                    "patient_id": (
                        chat.receiver.user.id
                        if chat.sender.user.id == request.user.id
                        else chat.sender.user.id
                    ),
                    "date": chat.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                }
                for chat in Message.objects.filter(
                    Q(sender__user__id=request.user.id)
                    | Q(receiver__user__id=request.user.id)
                )
                .prefetch_related("sender")
                .prefetch_related("receiver")
                .prefetch_related("sender__user")
                .prefetch_related("receiver__user")
            ]
        )

        return render(
            request,
            self.template_name,
            context={
                "patients": json.dumps(list(patients.values()), cls=DjangoJSONEncoder),
                "chats": chats,
                "access_token": str(token.access_token),
            },
        )


class TaskDashboardView(View):
    template_name = "pages/patient_details.html"

    def get(self, request):
        return render(request, self.template_name)


class VideoCallView(DoctorAuthMixin, View):
    template_name = "pages/video_call.html"

    def get(self, request, call_id):
        return render(
            request,
            self.template_name,
            {
                "call_id": call_id,
                "app_id": os.environ.get("ZEGO_APP_ID"),
                "app_secret": os.environ.get("ZEGO_SERVER_SECRET"),
                "room_id": call_id,
            },
        )
