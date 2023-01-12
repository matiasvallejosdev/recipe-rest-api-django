"""
Testing recipe models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from recipe_api.models import Recipe


class TestModels(TestCase):
    """Test creation of models for recipe_api."""

    def test_create_recipe(self):
        """Test create recipe is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testexample123'
        )
        recipe = Recipe.objects.create(
            user=user,
            title='Recipe title',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Recipe description'
        )
        self.assertEqual(str(recipe), recipe.title)
