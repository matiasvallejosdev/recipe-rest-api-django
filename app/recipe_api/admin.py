from django.contrib import admin
from recipe_api.models import Recipe, Tag

admin.site.register(Recipe)
admin.site.register(Tag)
