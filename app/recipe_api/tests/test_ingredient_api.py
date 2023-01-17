"""
Tests for ingredient API.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from recipe_api.models import Ingredient, Recipe
from recipe_api.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe_api:ingredient-list')


def get_detail_ingredient_url(ingredient_id):
    """Create and return ingredient detail URL."""
    return reverse('recipe_api:ingredient-detail', args=(ingredient_id,))


def create_user(email='user@example.com', password='testpassword123'):
    """Create user model."""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class PublicTestIngredientAPI(TestCase):
    """Testing unauthenticated APIs requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestIngredientAPI(TestCase):
    """Testing authenticated APIs requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieving_ingredients(self):
        """Test retrieve list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Ingredient1')
        Ingredient.objects.create(user=self.user, name='Ingredient2')
        Ingredient.objects.create(user=self.user, name='Ingredient3')
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(ingredients), len(res.data))
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_limited_to_user(self):
        """Test list of ingredients is limited to user."""
        other_user = create_user(email='newuser@example.com')
        ingredient = Ingredient.objects.create(user=self.user, name='Ingredient1')
        Ingredient.objects.create(user=other_user, name='Ingredient2')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_ingredients_success(self):
        """Test create ingredients successfully."""
        payload = {
            'name': 'Ingredient',
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(id=res.data['id']).exists()
        ingredient = Ingredient.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(ingredient, k), v)
        self.assertTrue(exists)
        self.assertEqual(ingredient.user, self.user)

    def test_create_normalized_ingredients(self):
        """Test if name of the ingredient was normalized."""
        payload = [{
            'name': 'ingredient'
        }, {
            'name': 'INGREDIENT'
        }]
        for item in payload:
            res = self.client.post(INGREDIENTS_URL, item)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            ingredient = Ingredient.objects.get(id=res.data['id'])
            self.assertEqual(ingredient.name, str(item['name']).capitalize())

    def test_create_ingredients_no_parameters_error(self):
        """Test creating with no parameter's error."""
        payload = {}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ingredient_success(self):
        """Test updating ingredient successfully."""
        ingredient = Ingredient.objects.create(user=self.user, name='Ingredient')
        payload = {
            'name': 'New name'
        }
        res = self.client.patch(get_detail_ingredient_url(ingredient.pk), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient_success(self):
        """Test delete ingredient successfully."""
        ingredient = Ingredient.objects.create(user=self.user, name='Ingredient')
        res = self.client.delete(get_detail_ingredient_url(ingredient.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(id=ingredient.pk).exists()
        self.assertFalse(ingredients)

    def test_trying_to_delete_ingredient_not_own(self):
        """Test trying to delete other user ingredient."""
        other_user = create_user(email='otheruser@example.com')
        ingredient = Ingredient.objects.create(user=other_user, name='Ingredient')
        res = self.client.delete(get_detail_ingredient_url(ingredient.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Ingredient.objects.filter(id=ingredient.pk).exists()
        self.assertTrue(exists)

    def test_trying_to_update_ingredient_not_own(self):
        """Test trying to update other user ingredient."""
        other_user = create_user(email='otheruser@example.com')
        payload = {
            'name': 'New name',
        }
        ingredient = Ingredient.objects.create(user=other_user, name='Ingredient')

        res = self.client.patch(get_detail_ingredient_url(ingredient.pk), payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        ingredient.refresh_from_db()
        self.assertNotEqual(ingredient.name, payload['name'])

    def test_ingredient_assign_to_recipes(self):
        """Test listing ingredients to those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredient_returns_unique_list(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
