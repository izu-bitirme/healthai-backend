from django.db import models


# Create your models here.
class Task(models.Model):
    user = models.ForeignKey("user_profile.UserProfile", on_delete=models.CASCADE)
    content = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    assigner = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="task_assigner",
    )
    percentage = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.content[:20]}"
