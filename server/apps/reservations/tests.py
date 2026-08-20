import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User, UserRole
from .models import Table, Reservation


class ReservationAPITests(APITestCase):

    def setUp(self):
        # Create Users
        self.admin = User.objects.create_user(
            username='admin_res',
            password='password123',
            role=UserRole.ADMIN
        )
        self.customer = User.objects.create_user(
            username='customer_res',
            password='password123',
            role=UserRole.CUSTOMER
        )

        # Create Table (Capacity: 4)
        self.table = Table.objects.create(table_number=1, capacity=4)

        self.table_url = reverse('table-list')
        self.reservation_url = reverse('reservation-list')

    def test_customer_can_create_reservation(self):
        """Ensure authenticated customer can book a valid table."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'table': self.table.id,
            'guest_count': 2,
            'reservation_date': str(datetime.date.today() + datetime.timedelta(days=1)),
            'reservation_time': '18:00:00',
            'special_requests': 'Window seat please'
        }

        response = self.client.post(self.reservation_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.first().customer, self.customer)

    def test_reservation_capacity_exceeded_fails(self):
        """Ensure booking guests exceeding table capacity fails with validation error."""
        self.client.force_authenticate(user=self.customer)
        payload = {
            'table': self.table.id,
            'guest_count': 6,  # Table capacity is 4
            'reservation_date': str(datetime.date.today() + datetime.timedelta(days=1)),
            'reservation_time': '18:00:00'
        }

        response = self.client.post(self.reservation_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('guest_count', response.data)

    def test_double_booking_prevention(self):
        """Ensure reserving an already booked table at the same date and time fails."""
        res_date = str(datetime.date.today() + datetime.timedelta(days=2))
        res_time = '19:00:00'

        # Existing Reservation
        Reservation.objects.create(
            customer=self.admin,
            table=self.table,
            guest_count=2,
            reservation_date=res_date,
            reservation_time=res_time,
            status='CONFIRMED'
        )

        self.client.force_authenticate(user=self.customer)
        payload = {
            'table': self.table.id,
            'guest_count': 2,
            'reservation_date': res_date,
            'reservation_time': res_time
        }

        response = self.client.post(self.reservation_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('table', response.data)