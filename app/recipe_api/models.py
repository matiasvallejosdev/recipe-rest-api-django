"""
Recipe models.
"""
from django.db import models
from django.conf import settings


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='images/recipes/', null=True, blank=True)
    time_minutes = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(max_length=255)
    link = models.URLField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    ingredients = models.ManyToManyField('Ingredient', blank=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tags for recipes object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = str(self.name).lower().replace(' ', '-')
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Tags for recipes object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = str(self.name).capitalize()
        return super(Ingredient, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
