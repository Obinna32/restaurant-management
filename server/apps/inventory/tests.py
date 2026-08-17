from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User, UserRole
from .models import Supplier, InventoryItem, StockTransaction


class InventoryAPITests(APITestCase):

    def setUp(self):
        # Create Users
        self.admin = User.objects.create_user(
            username='admin_inv',
            password='password123',
            role=UserRole.ADMIN
        )
        self.chef = User.objects.create_user(
            username='chef_inv',
            password='password123',
            role=UserRole.CHEF
        )
        self.customer = User.objects.create_user(
            username='customer_inv',
            password='password123',
            role=UserRole.CUSTOMER
        )

        # Create Supplier & Item
        self.supplier = Supplier.objects.create(name='Fresh Farms Co.')
        self.item = InventoryItem.objects.create(
            name='Tomatoes',
            quantity=5.00,
            unit='kg',
            reorder_level=10.00,
            cost_per_unit=2.50,
            supplier=self.supplier
        )

        self.item_list_url = reverse('inventory-item-list')
        self.low_stock_url = reverse('inventory-item-low-stock')
        self.log_trans_url = reverse('inventory-item-log-transaction', kwargs={'pk': self.item.pk})

    def test_customer_cannot_access_inventory(self):
        """Ensure customers cannot access inventory endpoints."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.item_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_low_stock_action(self):
        """Ensure item with quantity (5) below reorder level (10) appears in low-stock action."""
        self.client.force_authenticate(user=self.chef)
        response = self.client.get(self.low_stock_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tomatoes')
        self.assertTrue(response.data[0]['is_low_stock'])

    def test_log_stock_in_transaction(self):
        """Ensure logging restock increases quantity and records transaction log."""
        self.client.force_authenticate(user=self.admin)
        payload = {
            'transaction_type': 'IN',
            'quantity': 20.00,
            'notes': 'Weekly restock shipment'
        }

        response = self.client.post(self.log_trans_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 25.00)
        self.assertEqual(StockTransaction.objects.count(), 1)
        self.assertEqual(StockTransaction.objects.first().transaction_type, 'IN')

    def test_log_stock_out_insufficient_error(self):
        """Ensure logging usage greater than current stock fails with 400 error."""
        self.client.force_authenticate(user=self.chef)
        payload = {
            'transaction_type': 'OUT',
            'quantity': 50.00,
            'notes': 'Over-use attempt'
        }

        response = self.client.post(self.log_trans_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5.00)