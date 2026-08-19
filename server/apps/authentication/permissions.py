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


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Allows access to any staff member (ADMIN, MANAGER, CHEF, WAITER) or superusers.
    """
    def has_permission(self, request, view):
        staff_roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.CHEF, UserRole.WAITER]
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role in staff_roles or request.user.is_staff or request.user.is_superuser)
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