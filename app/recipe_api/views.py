"""
Views for recipe_api endpoint.
"""
from rest_framework import permissions
from rest_framework import viewsets

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
