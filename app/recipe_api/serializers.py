"""
Serializer for recipe_api.
"""
from rest_framework import serializers
from .models import Recipe

from user_api.serializers import UserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link',)
        read_only_fields = ('id',)


class RecipeDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'user', 'description',)
        read_only_fields = ('id',)
