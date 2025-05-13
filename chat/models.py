from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth import get_user_model


class Message(models.Model):
    TEXT = "text"
    IMAGE = "image"
    MESSAGE_TYPE_CHOICES = [
        (TEXT, "Text"),
        (IMAGE, "Image"),
    ]

    sender = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="received_messages",
    )

    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPE_CHOICES, default=TEXT
    )
    content = models.TextField(blank=True, null=True)
    image = ResizedImageField(
        size=[600, 600],
        crop=["middle", "center"],
        force_format="WEBP",
        quality=80,
        upload_to="chat_messages/",
        blank=True,
        null=True,
    )

    auto_delete_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


User = get_user_model()


class VideoCall(models.Model):
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="caller")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    call_id = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, default="initiated"
    )  # initiated, ongoing, completed

    def __str__(self):
        return f"Call {self.call_id} between {self.caller} and {self.receiver}"
