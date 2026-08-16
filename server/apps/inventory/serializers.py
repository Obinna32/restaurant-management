from rest_framework import serializers
from .models import Supplier, InventoryItem, StockTransaction


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class InventoryItemSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = (
            'id', 
            'name', 
            'quantity', 
            'unit', 
            'reorder_level', 
            'cost_per_unit', 
            'supplier', 
            'supplier_name', 
            'is_low_stock', 
            'last_restocked', 
            'created_at', 
            'updated_at'
        )


class StockTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = StockTransaction
        fields = (
            'id', 
            'item', 
            'item_name', 
            'transaction_type', 
            'quantity', 
            'notes', 
            'created_by', 
            'created_by_username', 
            'created_at'
        )
        read_only_fields = ('created_by',)