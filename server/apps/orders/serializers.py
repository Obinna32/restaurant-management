from rest_framework import serializers
from apps.menu.models import MenuItem
from .models import Order, OrderItem, Payment

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price', 'special_instructions')
        read_only_fields = ('unit_price',)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at')
        read_only_fields = ('amount', 'created_at')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment = PaymentSerializer(read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    table_number = serializers.IntegerField(source='table.table_number', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'customer',
            'customer_username',
            'table',
            'table_number',
            'order_type',
            'status',
            'total_amount',
            'items',
            'payment',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('customer', 'total_amount', 'status')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data.get('quantity', 1)
            special_instructions = item_data.get('special_instructions', '')
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                unit_price=menu_item.price,
                special_instructions=special_instructions
            )

        order.calculate_total()
        return order