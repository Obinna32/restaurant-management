from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, UserRole

# Create your tests here.
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.profile_url = reverse('auth_profile')

        self.user_data = {
            'username': 'john_customer',
            'email': 'johndoe@example.com',
            'password': 'password',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+2347032731522'
        }

    def test_user_registration(self):
        """Ensure a new customer can register successfully."""
        response = self.client.post(self.register_url, self.user_data)
        print("\nREGISTRATION ERROR RESPONSE:", response.data)  # <--- Temporary print line
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.get(username='john_customer')
        self.assertEqual(user.role, UserRole.CUSTOMER)

    def test_jwt_login_and_token_payload(self):
        #Ensure valid credentials return access/refresh tokens with role in response
        User.objects.create_user(**self.user_data)
        
        login_payload = {
            'username': 'john_customer',
            'password': 'password'
        }
        response = self.client.post(self.login_url, login_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], UserRole.CUSTOMER)

    def test_protected_profile_endpoint(self):
        #Ensure protected endpoint rejects unauthenticated requests and permits valid JWT token
        user = User.objects.create_user(**self.user_data)

        # Unauthenticated request
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated request
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'john_customer')