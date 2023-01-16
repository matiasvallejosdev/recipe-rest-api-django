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
                          TagDetailSerializer,
                          IngredientSerializer,
                          IngredientDetailSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
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
        if self.action == 'create' or self.action == 'update':
            return RecipeCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TagViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    model = Tag
    serializer_class = TagDetailSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return TagSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientViewSet(viewsets.ModelViewSet):
    model = Ingredient
    serializer_class = IngredientDetailSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def get_serializer_class(self):
        if self.action == 'list':
            return IngredientSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
