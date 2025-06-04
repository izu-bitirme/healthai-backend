from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification, UserProfile, Patient, Doctor, Therapist


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("message",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.first_name = user.first_name or user.username
        user.save()
        profile = UserProfile.objects.create(user=user, role=UserProfile.PATIENT)
        patient = Patient.objects.create(profile=profile)

        patient.doctors.add(Doctor.objects.all().order_by("?").first())

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("password", None)
        return data


class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="profile.user.username", read_only=True)
    full_name = serializers.CharField(
        source="profile.user.get_full_name", read_only=True
    )
    avatar = serializers.ImageField(source="profile.photo", read_only=True)
    userId = serializers.IntegerField(source="profile.user.id", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "userId",
            "username",
            "full_name",
            "specialty",
            "license_number",
            "avatar",
        ]

    def get_avatar(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.profile.photo.url)
        return obj.profile.photo.url


class TherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Therapist
        exclude = ["profile"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    days_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "role", "photo", "bio", "days_left"]

    def get_photo(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url

    def get_days_left(self, obj):
        if obj.role == UserProfile.PATIENT:
            patient = Patient.objects.get(profile=obj)
            return (datetime.now().date() - patient.start_date).days
        return 90


class PatientSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    doctors = DoctorSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"

    def get_profile(self, obj):
        return ProfileSerializer(
            obj.profile, context={"request": self.context.get("request")}
        ).data

    def get_doctors(self, obj):
        return DoctorSerializer(
            obj.doctors, many=True, context={"request": self.context.get("request")}
        ).data
