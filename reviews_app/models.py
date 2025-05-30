from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')
