from rest_framework import permissions


class IsCitizen(permissions.BasePermission):
    """
    Permission untuk memastikan hanya user dengan role Citizen/member
    yang dapat membuat laporan.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_member', False)
        )


class IsOwnerDraftOrAdminStatusOnly(permissions.BasePermission):
    """
    Permission untuk endpoint Report:
    - Read-only method seperti GET boleh untuk user yang sudah login.
    - Citizen hanya boleh update/delete laporan miliknya jika status masih DRAFT.
    - Admin hanya boleh update status, bukan delete.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        is_admin = getattr(request.user, 'is_admin', False) or request.user.is_superuser

        if is_admin:
            return request.method in ['PUT', 'PATCH']

        is_owner = obj.reporter == request.user
        is_draft = obj.status == 'DRAFT'

        return is_owner and is_draft