from django.contrib import admin
from .models import UserProfile, Doctor, Patient, Therapist

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "is_verified"]
    search_fields = ["user__username", "user__email"]

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["profile", "specialty", "license_number", "hospital"]
    search_fields = ["profile__user__username", "specialty"]

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["profile", "surgery_type"]


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ["profile", "expertise_area", "license_number"]
    search_fields = ["profile__user__username", "expertise_area"]
