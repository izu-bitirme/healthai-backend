from django.db import models
from django_resized import ResizedImageField


# Create your models here.
class UserProfile(models.Model):
    DOCTOR = "doctor"
    PATIENT = "patient"
    ROLE_CHOICES = [
        (DOCTOR, "doctor"),
        (PATIENT, "patient"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = ResizedImageField(
        size=[300, 300],
        crop=["middle", "center"],
        force_format="WEBP",
        quality=80,
        default="profiles/default.png",
        upload_to="profiles",
    )
    is_verified = models.BooleanField(default=False)
    full_address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
