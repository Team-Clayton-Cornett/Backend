from rest_framework.permissions import BasePermission

class IsAuthenticatedOrCreate(BasePermission):
    """
    Allows access only to authenticated users or for POST method.
    """

    def has_permission(self, request, view):
        if view.action == "create_user":
            return True

        return bool(request.user and request.user.is_authenticated)
