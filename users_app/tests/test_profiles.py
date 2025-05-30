from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token


class ProfileTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='business1', email='biz@example.com', password='testpass')
        self.customer_user = User.objects.create_user(
            username='customer1', email='cust@example.com', password='testpass')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='business1', type='business')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='customer1', type='customer')
        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

    def test_profile_get_by_id(self):
        url = reverse('profile-detail', kwargs={"pk": self.business_user.id})
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.business_user.id)

    def test_profile_patch_self(self):
        url = reverse('profile-detail', kwargs={"pk": self.customer_user.id})
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.patch(url, {"first_name": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_profile_patch_other_forbidden(self):
        url = reverse('profile-detail', kwargs={"pk": self.business_user.id})
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.patch(url, {"first_name": "Hacker"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_business_profiles(self):
        url = reverse('business-profiles')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["type"] == "business" for p in response.data))

    def test_list_customer_profiles(self):
        url = reverse('customer-profiles')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["type"] == "customer" for p in response.data))
