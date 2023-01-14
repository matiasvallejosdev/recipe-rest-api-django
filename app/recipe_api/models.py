"""
Recipe models.
"""
from django.db import models
from django.conf import settings


class Recipe(models.Model):
    """Recipe object."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(max_length=255)
    link = models.URLField(max_length=255, blank=True)

    def __str__(self):
        return self.title
