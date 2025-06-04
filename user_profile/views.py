from datetime import datetime
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from user_profile.forms import NotificationForm
from web.views import DoctorAuthMixin
from .models import Notification, UserProfile, Doctor, Patient, Therapist
from .serializers import (
    NotificationSerializer,
    ProfileSerializer,
    UserSerializer,
    DoctorSerializer,
    PatientSerializer,
    TherapistSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models import F, Sum, CharField, Value
from django.db.models.functions import Concat


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        request.data["first_name"] = request.data.get("username")
        request.data["username"] = request.data.get("email", "").split("@")[0]
        request.data["email"] = request.data.get("email", "")
        return super().create(request, *args, **kwargs)


class ProfileView(CreateAPIView, RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            user = User.objects.get(id=request.user.id)
            UserProfile.objects.create(user=user, role="patient")
            serializer = self.get_serializer(UserProfile.objects.get(user=request.user))
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

    def post(self, request, *args, **kwargs):
        try:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = self.get_serializer(
                user_profile, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                role = serializer.validated_data.get("role") or user_profile.role
                if created:
                    if role == UserProfile.DOCTOR:
                        Doctor.objects.get_or_create(profile=user_profile)
                    elif role == UserProfile.PATIENT:
                        Patient.objects.get_or_create(profile=user_profile)
                    elif role == UserProfile.THERAPIST:
                        Therapist.objects.get_or_create(profile=user_profile)

                status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response(serializer.data, status=status_code)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PatientProfileView(APIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = Patient.objects.get(profile__user=request.user)
            serializer = PatientSerializer(user_profile, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, *args, **kwargs):
        patient = Patient.objects.get(profile__user=request.user)
        patient.height_before = request.data.get("height_before", 170)
        patient.weight = request.data.get("weight", 70)
        patient.save()

        serializer = PatientSerializer(patient, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetDoctorsView(APIView):
    def get(self, request):
        doctors = Doctor.objects.annotate(
            full_name=Concat(
                F("profile__user__first_name"),
                Value(" "),
                F("profile__user__last_name"),
                output_field=CharField(),
            ),
            email=F("profile__user__email"),
            user_id=F("profile__user__id"),
        )
        serializer = DoctorSerializer(doctors, many=True, context={"request": request})
        return Response({"doctors": serializer.data}, status=status.HTTP_200_OK)


class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(
            Q(asigned_patient__profile__user=request.user)
            | Q(asigned_patient__isnull=True),
            valid_until__gte=datetime.now(),
        ).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"notifications": serializer.data}, status=status.HTTP_200_OK)


class NotificationView(DoctorAuthMixin, View):
    template_name = "pages/notifications.html"
    form_class = NotificationForm

    def get(self, request):
        doctor = Doctor.objects.filter(profile__user=request.user).first()

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
                "notifications": Notification.objects.filter(user=doctor).order_by(
                    "-created_at"
                ),
            },
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.data.get("asigned_patient", "0") == "0":
            _mutable = form.data._mutable
            form.data._mutable = True
            form.data["asigned_patient"] = None
            form.data._mutable = _mutable

        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = Doctor.objects.filter(profile__user=request.user).first()
            instance.save()

        return redirect(reverse("notifications"))
