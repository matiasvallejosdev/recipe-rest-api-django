"""
Views for recipe_api endpoint.
"""
from rest_framework import permissions
from rest_framework import viewsets

from .models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeViewset(viewsets.ModelViewSet):
    model = Recipe
    serializer_class = RecipeDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Returns serializer class for the request."""
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
