from rest_framework import viewsets, permissions
from apps.authentication.permissions import IsAdminUserRole, IsChefOrAdmin
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        # Anyone can view categories; only Admin/Chef can modify
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsChefOrAdmin]
        return [permission() for permission in permission_classes]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category_id = self.request.query_params.get('category', None)
        available_only = self.request.query_params.get('available', None)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if available_only is not None and available_only.lower() == 'true':
            queryset = queryset.filter(is_available=True)

        return queryset

    def get_permissions(self):
        # Anyone can view menu items; only Admin/Chef can create/edit/delete
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsChefOrAdmin]
        return [permission() for permission in permission_classes]