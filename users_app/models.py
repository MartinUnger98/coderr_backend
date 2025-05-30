from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='profile-images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=50, blank=True)

    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username
