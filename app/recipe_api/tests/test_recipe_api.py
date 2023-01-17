"""
Test for recipe_api.
"""
# import os
import tempfile

from PIL import Image

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from recipe_api.models import Recipe, Tag, Ingredient
from recipe_api.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe_api:recipe-list')


def recipes_detail_url(recipe_id):
    """Creates and return recipe details URL."""
    return reverse('recipe_api:recipe-detail', args=[recipe_id])


def recipes_thumbnail_upload_url(recipe_id):
    """Creates and return recipes image upload URL."""
    return reverse('recipe_api:recipe-upload-image', args=[recipe_id])


def create_ingredient(user, **params):
    payload = {
        'name': 'Ingredient'
    }
    payload.update(**params)
    return Ingredient.objects.create(user=user, **payload)


def create_tag(user, **params):
    payload = {
        'name': 'Tag1'
    }
    payload.update(**params)
    return Tag.objects.create(user=user, **payload)


def create_recipe(user, **params):
    payload = {
        'title': 'Sample title',
        'time_minutes': 4,
        'price': Decimal('1.50'),
        'description': 'Sample description',
        'link': 'https://example.com/recipe.pdf'
    }
    payload.update(params)
    return Recipe.objects.create(user=user, **payload)


class TestPublicRecipeAPI(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateRecipeAPI(TestCase):
    """Test authorized API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='userexample123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieve list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated users."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='password123'
        )
        create_recipe(user=self.user)
        create_recipe(user=other_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_get_recipe_detail(self):
        """Test get details of recipe."""
        recipe = create_recipe(user=self.user)
        res = self.client.get(recipes_detail_url(recipe.pk))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_success(self):
        """Create recipe with all parameters successfully."""
        payload = {
            'title': 'Sample title',
            'time_minutes': 3,
            'price': Decimal('1.50'),
            'description': 'Sample description',
            'link': 'https://example.com'
        }
        res = self.client.post(RECIPES_URL, payload)
        exists = Recipe.objects.filter(id=res.data['id']).exists()
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertTrue(exists)
        self.assertEqual(recipe.user, self.user)

    def test_perform_partial_update_recipe(self):
        """Partial update a recipe."""
        payload = {
            'title': 'New title',
            'time_minutes': 120
        }
        recipe = create_recipe(user=self.user)
        res = self.client.patch(recipes_detail_url(recipe.pk), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])

    def test_perform_fully_update_recipe(self):
        """Fully updated recipe."""
        payload = {
            'title': 'New title',
            'time_minutes': 133,
            'price': Decimal('1.0'),
            'description': 'New description',
            'link': 'https://newlink.com'
        }
        recipe = create_recipe(user=self.user)
        res = self.client.put(recipes_detail_url(recipe.pk), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_error_when_try_to_change_user(self):
        """Test try to change recipe user with error."""
        new_user = get_user_model().objects.create_user(email='newuser@example.com', password='password123')
        recipe = create_recipe(user=self.user)
        payload = {
            'user': new_user.pk
        }
        res = self.client.patch(recipes_detail_url(recipe.pk), payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Fully delete a recipe success."""
        recipe = create_recipe(user=self.user)
        res = self.client.delete(recipes_detail_url(recipe.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        recipes = Recipe.objects.filter(id=recipe.pk).exists()
        self.assertFalse(recipes)

    def test_try_to_update_other_user_recipe(self):
        """Test trying to update recipe with other user."""
        payload = {
            'title': 'New title',
            'time_minutes': 120
        }
        new_user = get_user_model().objects.create_user(email='newuser@example.com', password='password123')
        recipe = create_recipe(user=new_user)

        res = self.client.patch(recipes_detail_url(recipe.pk), payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        recipe.refresh_from_db()
        self.assertNotEqual(recipe.title, payload['title'])
        self.assertNotEqual(recipe.time_minutes, payload['time_minutes'])

    def test_try_to_delete_other_user_recipe(self):
        """Test trying to delete recipe with other user."""
        new_user = get_user_model().objects.create_user(email='newuser@example.com', password='password123')
        recipe = create_recipe(user=new_user)
        res = self.client.delete(recipes_detail_url(recipe.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Recipe.objects.filter(id=recipe.pk).exists()
        self.assertTrue(exists)

    def test_create_recipe_with_tags(self):
        """Test create a new recipe with multiples tags."""
        tag1 = create_tag(user=self.user, name='tag1')
        tag2 = create_tag(user=self.user, name='tag2')
        payload = {
            'title': 'Sample title',
            'time_minutes': 3,
            'price': Decimal('1.50'),
            'description': 'Sample description',
            'link': 'https://example.com',
            'tags': [tag1.pk, tag2.pk]
        }
        res = self.client.post(RECIPES_URL, payload)
        exists = Recipe.objects.filter(id=res.data['id']).exists()
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tags = recipe.tags.all()
        self.assertEqual(tags[0].pk, payload['tags'][0])
        self.assertEqual(tags[1].pk, payload['tags'][1])
        payload.pop('tags')
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertTrue(exists)
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_ingredients(self):
        """Test create a new recipe with multiples ingredients successfully."""
        ingredient1 = create_ingredient(user=self.user)
        ingredient2 = create_ingredient(user=self.user)
        payload = {
            'title': 'Sample title',
            'time_minutes': 3,
            'price': Decimal('1.50'),
            'description': 'Sample description',
            'link': 'https://example.com',
            'ingredients': [ingredient1.pk, ingredient2.pk]
        }
        res = self.client.post(RECIPES_URL, payload)
        exists = Recipe.objects.filter(id=res.data['id']).exists()
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients[0].pk, payload['ingredients'][0])
        self.assertEqual(ingredients[1].pk, payload['ingredients'][1])
        payload.pop('ingredients')
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertTrue(exists)
        self.assertEqual(recipe.user, self.user)

    def test_filter_recipes_by_tags(self):
        """Test filtering recipes using tags query params."""
        tag1 = create_tag(user=self.user, name='tag1')
        tag2 = create_tag(user=self.user, name='tag2')
        recipe1 = create_recipe(user=self.user, title='recipe1')
        recipe1.tags.add(tag1)
        recipe2 = create_recipe(user=self.user, title='recipe2')
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title='recipe3')  # no tags

        params = {
            'tags': f'{tag1.id}, {tag2.id}'
        }
        res = self.client.get(RECIPES_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer_recipe1 = RecipeSerializer(recipe1)
        serializer_recipe2 = RecipeSerializer(recipe2)
        serializer_recipe3 = RecipeSerializer(recipe3)

        self.assertEqual(len(res.data), 2)
        self.assertIn(serializer_recipe1.data, res.data)
        self.assertIn(serializer_recipe2.data, res.data)
        self.assertNotIn(serializer_recipe3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test filtering recipes using ingredients query params."""
        ingredient1 = create_ingredient(user=self.user, name='ingredient1')
        ingredient2 = create_ingredient(user=self.user, name='ingredient2')
        recipe1 = create_recipe(user=self.user, title='recipe1')
        recipe1.ingredients.add(ingredient1)
        recipe2 = create_recipe(user=self.user, title='recipe2')
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe(user=self.user, title='recipe3')  # no tags

        params = {
            'ingredients': f'{ingredient1.id}, {ingredient2.id}'
        }
        res = self.client.get(RECIPES_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer_recipe1 = RecipeSerializer(recipe1)
        serializer_recipe2 = RecipeSerializer(recipe2)
        serializer_recipe3 = RecipeSerializer(recipe3)

        self.assertEqual(len(res.data), 2)
        self.assertIn(serializer_recipe1.data, res.data)
        self.assertIn(serializer_recipe2.data, res.data)
        self.assertNotIn(serializer_recipe3.data, res.data)


class TestImageUpload(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        # self.recipe.thumbnail.delete()
        pass

    def test_upload_recipe_thumbnail_image(self):
        """Test uploading an image to a recipe thumbnail image."""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'thumbnail': image_file
            }
            res = self.client.post(recipes_thumbnail_upload_url(self.recipe.id),
                                   payload,
                                   format='multipart')
            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('thumbnail', res.data)
            # self.assertTrue(os.path.exists(self.recipe.thumbnail.path))

    def test_upload_invalid_recipe_thumbnail_image(self):
        """Test uploading an invalid image to a recipe with error."""
        payload = {}
        res = self.client.post(recipes_thumbnail_upload_url(self.recipe.id),
                               payload,
                               format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
