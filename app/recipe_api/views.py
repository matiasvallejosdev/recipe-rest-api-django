"""
Views for recipe_api endpoint.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Recipe, Tag, Ingredient
from .serializers import (RecipeCreateSerializer,
                          RecipeSerializer,
                          RecipeDetailSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeImageSerializer)


class BaseRecipeAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for recipe attributes."""
    permission_classes = (permissions.IsAuthenticated,)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
class BaseIngredientTagAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for ingredients and tags attributes."""
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Retrieve ingredients or tags only for authenticated user."""
        assigned_only = bool(self.request.query_params.get('assigned_only', 0))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
class RecipeViewSet(BaseRecipeAttrViewSet):
    model = Recipe
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def _params_to_ints(self, qs):
        """Convert string into a list of integers."""
        return [int(param_id) for param_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user filtered by tags and ingredients."""
        tags = self.request.query_params.get('tags', None)
        ingredients = self.request.query_params.get('ingredients', None)
        queryset = self.queryset.filter(user=self.request.user)
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        """Returns serializer class for the request."""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'create' or self.action == 'update':
            return RecipeCreateSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
