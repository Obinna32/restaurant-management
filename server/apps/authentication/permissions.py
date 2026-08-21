from rest_framework import permissions
from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with the ADMIN role or Django superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


# Alias for backward compatibility
IsAdminUserRole = IsAdmin


class IsChefOrAdmin(permissions.BasePermission):
    """
    Allows access to users with CHEF or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role in [UserRole.CHEF, UserRole.ADMIN] or request.user.is_superuser)
        )


class IsWaiterOrAdmin(permissions.BasePermission):
    """
    Allows access to users with WAITER or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role in [UserRole.WAITER, UserRole.ADMIN] or request.user.is_superuser)
        )


from rest_framework import permissions
from .models import UserRole


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow access only to staff members.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Access roles via defined attributes or standard staff values
        allowed_roles = getattr(UserRole, 'STAFF', None)
        staff_roles = [UserRole.ADMIN, UserRole.CHEF, UserRole.WAITER]
        if allowed_roles:
            staff_roles.append(allowed_roles)

        return request.user.role in staff_roles or request.user.is_staff


class IsCustomer(permissions.BasePermission):
    """
    Allows access only to registered CUSTOMER users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == UserRole.CUSTOMER
        )