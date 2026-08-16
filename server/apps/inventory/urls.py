from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, InventoryItemViewSet, StockTransactionViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'items', InventoryItemViewSet, basename='inventory-item')
router.register(r'transactions', StockTransactionViewSet, basename='stock-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
