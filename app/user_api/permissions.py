"""
Permissions personalized for users.
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        print(request.user)
        return False