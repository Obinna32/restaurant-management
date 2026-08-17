from decimal import Decimal, InvalidOperation
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.authentication.permissions import IsChefOrAdmin
from .models import Supplier, InventoryItem, StockTransaction
from .serializers import (
    SupplierSerializer, 
    InventoryItemSerializer, 
    StockTransactionSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsChefOrAdmin]


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsChefOrAdmin]

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Custom endpoint to list only items below reorder level."""
        low_items = [item for item in self.get_queryset() if item.is_low_stock]
        serializer = self.get_serializer(low_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def log_transaction(self, request, pk=None):
        """Custom action to log stock additions/deductions and auto-update quantity."""
        item = self.get_object()
        trans_type = request.data.get('transaction_type')
        qty = request.data.get('quantity')
        notes = request.data.get('notes', '')

        if not trans_type or not qty:
            return Response(
                {'error': 'transaction_type and quantity are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            qty = Decimal(str(qty))
        except (ValueError, InvalidOperation):
            return Response({'error': 'Quantity must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update Inventory Quantity
        if trans_type == 'IN':
            item.quantity += qty
            item.last_restocked = timezone.now()
        elif trans_type in ['OUT', 'WASTE']:
            if item.quantity < qty:
                return Response(
                    {'error': 'Insufficient inventory quantity available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity -= qty
        else:
            return Response({'error': 'Invalid transaction type.'}, status=status.HTTP_400_BAD_REQUEST)

        item.save()

        # Create audit log transaction
        transaction = StockTransaction.objects.create(
            item=item,
            transaction_type=trans_type,
            quantity=qty,
            notes=notes,
            created_by=request.user
        )

        return Response({
            'message': 'Stock updated successfully.',
            'current_quantity': item.quantity,
            'transaction': StockTransactionSerializer(transaction).data
        }, status=status.HTTP_200_OK)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.all().order_by('-created_at')
    serializer_class = StockTransactionSerializer
    permission_classes = [IsChefOrAdmin]