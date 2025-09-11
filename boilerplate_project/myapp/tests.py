from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status


class ListUsersTests(APITestCase):
    def setUp(self):
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123'
        )
        self.regular_user_token = Token.objects.create(user=self.regular_user)

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='adminpass123'
        )
        self.admin_user_token = Token.objects.create(user=self.admin_user)

        # Create some test users to list
        User.objects.create_user(username='test_user1')
        User.objects.create_user(username='test_user2')

        # URL for our endpoint
        self.url = reverse('list-users')

    def test_unauthenticated_access(self):
        """Test that unauthenticated access is denied"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access(self):
        """Test that non-admin users cannot access the endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_user_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access(self):
        """Test that admin users can access the endpoint and get correct data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_user_token.key}')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)  # Our 4 users: regular, admin, test1, test2

        # Check that all usernames are in the response
        expected_usernames = {'regular_user', 'admin_user', 'test_user1', 'test_user2'}
        self.assertEqual(set(response.data), expected_usernames)
