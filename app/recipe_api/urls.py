"""
URLs mapping for recipe_api.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

app_name = 'recipe_api'
urlpatterns = [
    path('', include(router.urls))
]
