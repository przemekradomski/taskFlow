from django.conf import settings
from django.db import models

class Issue(models.Model):
    class Status(models.TextChoices):
        TO_DO = "To Do", "Do zrobienia"
        IN_PROGRESS = "In Progress", "W Trakcie"
        DONE = "Done", "Gotowe"
    class Priority(models.TextChoices):
        LOW = "Low", "Niska",
        MEDIUM = "Medium", "Średnia",
        HIGH = "High", "Wysoka",
        URGENT = "Urgent", "Pilna"

    title = models.CharField(max_length=100)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_DO
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
    )

    def __str__(self):
        return self.title

class AccountVerification(models.Model):

    CODE_VALIDITY_HOURS = 24

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification",
    )
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta

        return timezone.now() - self.created_at > timedelta(
            hours=self.CODE_VALIDITY_HOURS
        )

    def __str__(self):
        return f"Weryfikacja: {self.user.username}"

class Profile(models.Model):


    ALLOWED_AVATAR_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.FileField(
        upload_to="avatars/%Y/%m/", blank=True, null=True
    )

    def __str__(self):
        return f"Profil: {self.user.username}"
