"""
Testing recipe models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from recipe_api.models import Recipe, Tag, Ingredient


def create_user():
    """Create user model."""
    return get_user_model().objects.create_user(
        email='user@example.com',
        password='testexample123'
    )


class TestModels(TestCase):
    """Test creation of models for recipe_api."""

    def test_create_recipe(self):
        """Test create recipe is successful."""
        user = create_user()
        recipe = Recipe.objects.create(
            user=user,
            title='Recipe title',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Recipe description'
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create tags is successfully."""
        user = create_user()
        tag = Tag.objects.create(
            user=user,
            name='tag1'
        )
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test create ingredient is successfully."""
        user = create_user()
        ingredient = Ingredient.objects.create(
            user=user,
            name='Ingredient name'
        )
        self.assertEqual(str(ingredient), ingredient.name)
