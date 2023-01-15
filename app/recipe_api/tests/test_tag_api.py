"""
Test for tags.
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from recipe_api.models import Tag
from recipe_api.serializers import TagSerializer, TagDetailSerializer

TAGS_URL = reverse('recipe_api:tag-list')


def tag_detail_url(tag_id):
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

        tags = Tag.objects.all().order_by('-id')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags are limited to user."""
        other_user = create_user(email='other@example.com')
        create_tag(user=self.user)
        create_tag(user=other_user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-id')
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

    def test_perform_update(self):
        """Test tag updated successfully."""
        tag = create_tag(user=self.user, name='my-tag')
        payload = {
            'name': 'my-new-name'
        }
        res = self.client.patch(tag_detail_url(tag.pk), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test tag is being deleted successfully."""
        tag = create_tag(user=self.user, name='my-tag')
        res = self.client.delete(tag_detail_url(tag.pk))
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

        res = self.client.patch(tag_detail_url(tag.pk), payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        tag.refresh_from_db()
        self.assertNotEqual(tag.name, payload['name'])

    def test_try_to_delete_other_user_tag(self):
        """Test trying to delete recipe with other user."""
        new_user = create_user(email='newuser@example.com')
        tag = create_tag(user=new_user)
        res = self.client.delete(tag_detail_url(tag.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Tag.objects.filter(id=tag.pk).exists()
        self.assertTrue(exists)
