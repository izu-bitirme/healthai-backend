from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Patient, Doctor, Therapist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        profile = UserProfile.objects.create(user=user, role=UserProfile.PATIENT)
        Patient.objects.create(profile=profile)
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
    userId = serializers.IntegerField(source="profile.user.id", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "userId",
            "username",
            "full_name",
            "specialty",
            "license_number",
        ]


class TherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Therapist
        exclude = ["profile"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "role",
            "photo",
            "bio",
        ]


class PatientSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    doctors = DoctorSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"
