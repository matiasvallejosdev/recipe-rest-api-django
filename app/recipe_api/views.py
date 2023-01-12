"""
Views for recipe_api endpoint.
"""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, permissions
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSerializer


class RecipeViewset(viewsets.ModelViewSet):
    model = Recipe
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')


