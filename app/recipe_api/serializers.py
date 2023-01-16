"""
Serializer for recipe_api.
"""
from rest_framework import serializers
from .models import Recipe, Tag, Ingredient

from user_api.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'user',)
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'user',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link',)
        read_only_fields = ('id',)


class RecipeDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'user', 'description', 'tags', 'ingredients',)
        read_only_fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all(), required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'user', 'description', 'tags', 'ingredients',)
        read_only_fields = ('id',)

class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'thumbnail', )
        read_only_fields = ('id',)
        extra_kwargs = {'thumbnail': {'required': 'True'}}