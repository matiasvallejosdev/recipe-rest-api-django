"""
Serializer for recipe_api.
"""
from rest_framework import serializers
from .models import Recipe

from user_api.serializers import UserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('id',)
