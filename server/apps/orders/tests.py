from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User, UserRole
from apps.menu.models import Category, MenuItem
from .models import Order, OrderItem, Payment


class OrderAPITests(APITestCase):

    def setUp(self):
        # Create Users
        self.admin = User.objects.create_user(
            username='admin_order',
            password='password123',
            role=UserRole.ADMIN
        )
        self.customer = User.objects.create_user(
            username='customer_order',
            password='password123',
            role=UserRole.CUSTOMER
        )

        # Create Category & Menu Item (removed invalid 'slug' fields)
        self.category = Category.objects.create(name='Main Course')
        self.menu_item = MenuItem.objects.create(
            category=self.category,
            name='Pasta Carbonara',
            price=Decimal('15.50'),
            is_available=True
        )

        self.orders_url = reverse('order-list')

    def test_customer_can_create_order(self):
        """Ensure authenticated customer can place an order and total amount is calculated correctly."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'order_type': 'DINE_IN',
            'items': [
                {
                    'menu_item': self.menu_item.id,
                    'quantity': 2,
                    'special_instructions': 'Extra cheese'
                }
            ]
        }

        response = self.client.post(self.orders_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, Decimal('31.00'))  # 2 * 15.50

    def test_staff_can_update_order_status(self):
        """Ensure staff can update order status."""
        order = Order.objects.create(customer=self.customer, order_type='DINE_IN')
        OrderItem.objects.create(order=order, menu_item=self.menu_item, quantity=1, unit_price=self.menu_item.price)
        order.calculate_total()

        self.client.force_authenticate(user=self.admin)
        url = reverse('order-update-status', kwargs={'pk': order.id})
        payload = {'status': 'PREPARING'}

        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'PREPARING')

    def test_process_payment(self):
        """Ensure payment processing marks order as completed."""
        order = Order.objects.create(customer=self.customer, order_type='TAKEAWAY', total_amount=Decimal('15.50'))
        payment = Payment.objects.create(order=order, amount=order.total_amount, status='PENDING')

        self.client.force_authenticate(user=self.customer)
        url = reverse('payment-process-payment', kwargs={'pk': payment.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(order.status, 'COMPLETED')