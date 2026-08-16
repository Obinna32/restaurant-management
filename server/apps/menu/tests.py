from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User, UserRole
from .models import Category, MenuItem

# Create your tests here.
class MenuAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username = 'adminuser',
            password = 'password123',
            role = UserRole.ADMIN
        )
        self.customer = User.objects.create_user(
            username = 'customeruser',
            password = 'password123',
            role = UserRole.CUSTOMER
        )

        self.category = Category.objects.create(
            name = 'Appetizers',
            description = 'Starters and light bites'
        )
        self.menu_item = MenuItem.objects.create(
            category = self.category,
            name = 'Garlic Bread',
            description = "Toasted bread with garlic butter",
            price = '6299',
            is_available = True
        )
        self.category_list_url = reverse('category-list')
        self.item_list_url = reverse('menu-item-list')

    def test_public_can_list_categories_and_items(self):
        #ensure unauthenticated users can view categories and mnu items
        cat_response = self.client.get(self.category_list_url)
        item_response = self.client.get(self.item_list_url)

        self.assertEqual(cat_response.status_code, status.HTTP_200_OK)
        self.assertEqual(item_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cat_response.data), 1)
        self.assertEqual(len(item_response.data), 1)

    def test_customer_cannnot_create_category(self):
        #Ensures non-staff/non-admin users cannot create menu categories
        self.client.force_authenticate(user=self.customer)
        payload = {'name': 'Desserts', 'description': 'Sweet treats'}

        response = self.client.post(self.category_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_category_and_item(self):
        #Ensure admin can create categories and menu items
        self.client.force_authenticate(user=self.admin)

        cat_payload = {'name': 'Main Course', 'description': 'Filling dishes'}
        cat_response = self.client.post(self.category_list_url, cat_payload)
        self.assertEqual(cat_response.status_code, status.HTTP_201_CREATED)

        item_payload = {
            'category': cat_response.data['id'],
            'name': 'Steak',
            'description': 'Grilled ribeye',
            'price': '38000.00',
            'is_available': True,
            'preparation_time_minutes' : 20
        }
        item_response = self.client.post(self.item_list_url, item_payload)
        self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 2)

    def test_item_filtering_by_category(self):
        #Ensures items can be filtered by category ID
        cat2 = Category.objects.create(name='Drinks')
        MenuItem.objects.create(category=cat2, name='Soda', price='500')

        response = self.client.get(f"{self.item_list_url}?category={cat2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Soda')