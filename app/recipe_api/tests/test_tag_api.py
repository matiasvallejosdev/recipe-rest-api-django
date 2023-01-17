"""
Test for tags.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from recipe_api.models import Tag, Recipe
from recipe_api.serializers import TagSerializer

TAGS_URL = reverse('recipe_api:tag-list')


def get_detail_tag_url(tag_id):
    return reverse('recipe_api:tag-detail', args=[tag_id])


def create_tag(user, **params):
    payload = {
        'name': 'Tag1'
    }
    payload.update(**params)
    return Tag.objects.create(user=user, **payload)


def create_user(**user):
    payload = {
        'email': 'test@example.com',
        'password': 'test123'
    }
    payload.update(**user)
    user = get_user_model().objects.create_user(**payload)
    return user


class PublicTestTagAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestTagAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_list_tags(self):
        """Test retrieve a list of tags."""
        create_tag(user=self.user, name='tag1')
        create_tag(user=self.user, name='tag2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags are limited to user."""
        other_user = create_user(email='other@example.com')
        create_tag(user=self.user)
        create_tag(user=other_user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_create_tag_successfully(self):
        """Test create new tag with API."""
        payload = {
            'name': 'tag1'
        }
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(id=res.data['id']).exists()
        tag = Tag.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(tag, k), v)
        self.assertTrue(exists)
        self.assertEqual(tag.user, self.user)

    def test_create_tag_normalized(self):
        """Test if the tag is being normalized during creation."""
        payload = {
            'name': 'TAG 1'
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tag = Tag.objects.get(id=res.data['id'])
        self.assertEqual(tag.name, 'tag-1')

    def test_perform_tag_update(self):
        """Test tag updated successfully."""
        tag = create_tag(user=self.user, name='my-tag')
        payload = {
            'name': 'my-new-name'
        }
        res = self.client.patch(get_detail_tag_url(tag.pk), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag_success(self):
        """Test tag is being deleted successfully."""
        tag = create_tag(user=self.user, name='my-tag')
        res = self.client.delete(get_detail_tag_url(tag.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(id=tag.pk).exists()
        self.assertFalse(tags)

    def test_try_to_update_other_user_tag(self):
        """Test trying to update tag with other user."""
        payload = {
            'name': 'tag-new',
        }
        new_user = create_user(email='newuser@example.com')
        tag = create_tag(user=new_user)

        res = self.client.patch(get_detail_tag_url(tag.pk), payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        tag.refresh_from_db()
        self.assertNotEqual(tag.name, payload['name'])

    def test_try_to_delete_other_user_tag(self):
        """Test trying to delete recipe with other user."""
        new_user = create_user(email='newuser@example.com')
        tag = create_tag(user=new_user)
        res = self.client.delete(get_detail_tag_url(tag.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Tag.objects.filter(id=tag.pk).exists()
        self.assertTrue(exists)

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=Decimal('5.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)