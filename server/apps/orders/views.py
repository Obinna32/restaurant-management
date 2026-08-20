from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.authentication.models import UserRole
from apps.authentication.permissions import IsStaffOrAdmin
from .models import Order, Payment
from .serializers import OrderSerializer, PaymentSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.CHEF, UserRole.WAITER]:
            queryset = Order.objects.all()
            status_param = self.request.query_params.get('status')
            if status_param:
                queryset = queryset.filter(status=status_param)
            return queryset
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        self._broadcast_order_update(order)

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffOrAdmin])
    def update_status(self, request, pk=None):
        """Allows Kitchen/Staff to advance order status (PENDING -> PREPARING -> READY -> SERVED -> COMPLETED)."""
        order = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        self._broadcast_order_update(order)

        return Response({
            'message': f'Order #{order.id} status updated to {new_status}.',
            'order': OrderSerializer(order).data
        })

    def _broadcast_order_update(self, order):
        """Pushes real-time WebSocket notifications to staff channel."""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'orders_updates',
                {
                    'type': 'order_update',
                    'order': OrderSerializer(order).data
                }
            )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Simulates processing payment for an order."""
        payment = self.get_object()
        if payment.status == 'COMPLETED':
            return Response({'error': 'Payment already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = 'COMPLETED'
        payment.transaction_id = f"TXN-{payment.order.id}-99"
        payment.save()

        # Mark order completed if paid
        order = payment.order
        order.status = 'COMPLETED'
        order.save()

        return Response({
            'message': 'Payment successful.',
            'payment': PaymentSerializer(payment).data
        })