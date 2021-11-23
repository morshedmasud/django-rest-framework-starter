from rest_framework import permissions


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.id == 1


class IsBoardMember(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.id == 2


class IsEditor(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.id == 3


class IsMember(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.id == 4


class IsExpensePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = ['PATCH', 'POST', 'PUT', 'DELETE']
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in method:
            return request.user.role.id < 4


class IsDonationPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = ['PATCH', 'POST', 'PUT', 'DELETE']
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in method:
            return request.user.role.id < 4


class IsCampaignPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = ['PATCH', 'POST', 'PUT', 'DELETE']
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in method:
            return request.user.role.id < 4


class IsUsersPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = ['PATCH', 'POST', 'PUT']
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in method:
            return request.user.role.id <= 4