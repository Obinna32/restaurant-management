from rest_framework import permissions
from .models import UserRole


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users with the ADMIN role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN
        )


class IsChefOrAdmin(permissions.BasePermission):
    """
    Allows access to users with CHEF or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.CHEF, UserRole.ADMIN]
        )


class IsWaiterOrAdmin(permissions.BasePermission):
    """
    Allows access to users with WAITER or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.WAITER, UserRole.ADMIN]
        )


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