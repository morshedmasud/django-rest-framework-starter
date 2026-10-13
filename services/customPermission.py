from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Object-level: the object's `user` field must be the requesting user."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsSelfOrAdmin(permissions.BasePermission):
    """Object-level for user objects: users can act on their own account, staff on any."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
