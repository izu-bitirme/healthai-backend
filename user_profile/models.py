from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField


class UserProfile(models.Model):
    # Roller
    DOCTOR = "doctor"
    PATIENT = "patient"
    THERAPIST = "therapist"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (DOCTOR, "Doctor"),
        (PATIENT, "Patient"),
        (THERAPIST, "Therapist"),
        (ADMIN, "Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Ortak alanlar
    photo = ResizedImageField(
        size=[300, 300],
        crop=["middle", "center"],
        force_format="WEBP",
        quality=80,
        default="profiles/default.png",
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    full_address = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Patient(models.Model):
    profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="patient_data"
    )

    height_before = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_target = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    surgery_date = models.DateField(null=True, blank=True)
    surgery_type = models.CharField(max_length=100, null=True, blank=True)
    blood_type = models.CharField(max_length=5, null=True, blank=True)
    allergies = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)

    doctors = models.ManyToManyField("Doctor", related_name="patients", blank=True)

    def __str__(self):
        return f"Patient: {self.profile.user.get_full_name()}"


class Doctor(models.Model):
    profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="doctor_data"
    )

    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    hospital = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.profile.user.get_full_name()}"


class Therapist(models.Model):
    profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="therapist_data"
    )

    expertise_area = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Therapist: {self.profile.user.get_full_name()}"
