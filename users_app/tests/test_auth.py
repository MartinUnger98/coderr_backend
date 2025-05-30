from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token


class AuthTests(APITestCase):
    def setUp(self):
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')

    def test_registration_success(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass1234",
            "repeated_password": "pass1234",
            "type": "customer"
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_registration_password_mismatch(self):
        data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "pass1234",
            "repeated_password": "wrongpass",
            "type": "customer"
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass1234')
        Token.objects.create(user=user)
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "pass1234"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_failure(self):
        response = self.client.post(
            self.login_url, {"username": "fakeuser", "password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_existing_username(self):
        User.objects.create_user(
            username="existing", email="e@x.com", password="pass")
        data = {
            "username": "existing",
            "email": "new@x.com",
            "password": "123456",
            "repeated_password": "123456",
            "type": "customer"
        }
        response = self.client.post(self.registration_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["username"][0],
            "Ein Benutzer mit diesem Benutzernamen existiert bereits."
        )

    def test_registration_with_existing_email(self):
        User.objects.create_user(
            username="uniqueuser", email="duplicate@example.com", password="pass")
        data = {
            "username": "newuser",
            "email": "duplicate@example.com",
            "password": "123456",
            "repeated_password": "123456",
            "type": "customer"
        }
        response = self.client.post(self.registration_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email"][0],
            "Ein Benutzer mit dieser E-Mail-Adresse existiert bereits."
        )
