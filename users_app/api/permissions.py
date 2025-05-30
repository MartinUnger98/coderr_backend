from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow only the owner of an object to edit it.

    - Read permissions are allowed to any request (GET, HEAD, OPTIONS).
    - Write permissions are only allowed to the user who owns the object.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
