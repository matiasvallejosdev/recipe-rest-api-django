"""
Serializer for recipe_api.
"""
from rest_framework import serializers
from .models import Recipe, Tag, Ingredient

from user_api.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class IngredientDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'user',)
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class TagDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
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

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'user', 'description', 'tags',)
        read_only_fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all(), required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'user', 'description', 'tags', 'ingredients',)
        read_only_fields = ('id',)
