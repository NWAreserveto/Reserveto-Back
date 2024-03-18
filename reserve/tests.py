# reserve/tests.py
from django.test import TestCase
from rest_framework import status
import uuid
from django.urls import reverse
from .models import *
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
# from .views import send_verification_email
from unittest.mock import patch


class LoginAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='Password123')
        self.customer = Customer.objects.create(user=self.user)
        
    def test_login_valid_credentials(self):
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'Password123'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['role'], 'customer')

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, 401)

class BarberSignupAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'user': {
                'username': 'testbarber',
                'email': 'barber@test.com',
                'password': 'Mohammad13822003',
                'confirm_password': 'Mohammad13822003'
            },
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
        }

    def test_barber_signup_valid_credentials(self):
        response = self.client.post('/api/BarberSignup/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('barber', response.data)
        self.assertEqual(response.data['barber']['first_name'], 'John')
        self.assertEqual(response.data['barber']['last_name'], 'Doe')

    def test_barber_signup_duplicate_user(self):
        existing_user = User.objects.create_user(username='testbarber', email='barber@test.com', password='Password123')
        response = self.client.post('/api/BarberSignup/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_barber_signup_missing_field(self):
        invalid_data = self.valid_data.copy()
        del invalid_data['first_name']
        response = self.client.post('/api/BarberSignup/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)  


class CustomerSignupAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'user': {
                'username': 'testcustomer',
                'email': 'customer@test.com',
                'password': 'Mohammad13822003',
                'confirm_password': 'Mohammad13822003'
            },
        }

    def test_customer_signup_valid_credentials(self):
        response = self.client.post('/api/CustomerSignup/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('customer', response.data)


    def test_customer_signup_duplicate_user(self):
        existing_user = User.objects.create_user(username='testcustomer', email='customer@test.com', password='Password123')
        response = self.client.post('/api/CustomerSignup/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_customer_signup_missing_field(self):
        invalid_data = self.valid_data.copy()
        del invalid_data['user']['username']
        response = self.client.post('/api/CustomerSignup/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
    

class PasswordResetAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='hosseinkhosroabadi45@gmail.com', password='password123')
        self.password_reset = PasswordReset.objects.create(user=self.user)

    def test_reset_password_valid_token(self):
        url = reverse('password_reset', kwargs={'token': self.password_reset.token})
        data = {'password': 'newpassword123', 'confirm_password': 'newpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(username='testuser').check_password('newpassword123'), True)

    def test_reset_password_invalid_token(self):
        invalid_token = str(uuid.uuid4())
        url = reverse('password_reset', kwargs={'token': invalid_token})
        data = {'password': 'newpassword123', 'confirm_password': 'newpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_mismatched_passwords(self):
        url = reverse('password_reset', kwargs={'token': self.password_reset.token})
        data = {'password': 'newpassword123', 'confirm_password': 'mismatchedpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# class EmailVerificationTestCase(TestCase):
#     @patch('reserve.views.send_mail')
#     def test_send_verification_email(self, mock_send_mail):
#         user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')  # Create a test user
#         send_verification_email(user)

#         # Check that send_mail was called with the correct arguments
#         mock_send_mail.assert_called_once_with(
#             'Subject',
#             'Message',
#             'from@example.com',
#             ['to@example.com'],
#             fail_silently=False,
#         )
