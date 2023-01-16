"""
Views for recipe_api endpoint.
"""
from rest_framework import permissions
from rest_framework import viewsets, mixins

from .models import Recipe, Tag, Ingredient
from .serializers import (RecipeCreateSerializer,
                          RecipeSerializer,
                          RecipeDetailSerializer,
                          TagSerializer,
                          IngredientSerializer)

class BaseRecipeAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for recipe attributes."""
    permission_classes = (permissions.IsAuthenticated,)

class BaseIngredientTagAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for ingredients and tags attributes."""
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Retrieve ingredients or tags only for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class RecipeViewSet(BaseRecipeAttrViewSet):
    model = Recipe
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Returns serializer class for the request."""
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'create' or self.action == 'update':
            return RecipeCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TagViewSet(BaseIngredientTagAttrViewSet):
    model = Tag
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientViewSet(BaseIngredientTagAttrViewSet):
    model = Ingredient
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
