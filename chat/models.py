from django.db import models
from django_resized import ResizedImageField


# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(
        "user_profile.UserProfile", on_delete=models.CASCADE, related_name="sender"
    )
    receiver = models.ForeignKey(
        "user_profile.UserProfile", on_delete=models.CASCADE, related_name="receiver"
    )
    seen = models.BooleanField(default=False)
    auto_delete_date = models.DateTimeField(null=True, blank=True)
    content = models.TextField()
    image = ResizedImageField(
        size=[600, 600],
        crop=["middle", "center"],
        force_format="WEBP",
        quality=80,
        upload_to="chat_messages/",
    )
    created_at = models.DateTimeField(auto_now_add=True)
