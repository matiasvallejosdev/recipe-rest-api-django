"""
URLs mapping for recipe_api.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RecipeViewset

router = DefaultRouter()
router.register('', RecipeViewset)

app_name = 'recipe_api'
urlpatterns = [
    path('', include(router.urls))
]
