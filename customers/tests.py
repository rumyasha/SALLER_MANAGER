from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer

class CustomerTests(APITestCase):
    def setUp(self):
        self.customer_data = {
            'full_name': 'Тестовый Клиент',
            'email': 'test@example.com',
            'phone': '+77771234567'
        }
        self.customer = Customer.objects.create(**self.customer_data)

    def test_create_customer(self):
        url = reverse('customer-list')
        response = self.client.post(url, self.customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_get_customer(self):
        url = reverse('customer-detail', args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.customer.email)