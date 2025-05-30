from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from offers_app.models import Offer
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token


class OfferPermissionTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz', password='testpass')
        self.customer_user = User.objects.create_user(
            username='cust', password='testpass')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='biz', type='business')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='cust', type='customer')
        self.token_business = Token.objects.create(user=self.business_user)
        self.token_customer = Token.objects.create(user=self.customer_user)

        self.offer_payload = {
            "title": "Grafikdesign-Paket",
            "image": None,
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium"
                }
            ]
        }

    def test_unauthenticated_user_cannot_create_offer(self):
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_user_cannot_create_offer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_creator_can_patch_offer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        create_resp = self.client.post(
            reverse('offers-list'), self.offer_payload, format='json')
        offer_id = create_resp.data['id']

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        url = reverse('offer-detail-update-delete', kwargs={'id': offer_id})
        patch_resp = self.client.patch(
            url, {'title': 'Hacker Title'}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_creator_can_delete_offer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        create_resp = self.client.post(
            reverse('offers-list'), self.offer_payload, format='json')
        offer_id = create_resp.data['id']

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        url = reverse('offer-detail-update-delete', kwargs={'id': offer_id})
        delete_resp = self.client.delete(url)
        self.assertEqual(delete_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_can_patch_and_delete(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        create_resp = self.client.post(
            reverse('offers-list'), self.offer_payload, format='json')
        offer_id = create_resp.data['id']

        url = reverse('offer-detail-update-delete', kwargs={'id': offer_id})
        patch_resp = self.client.patch(
            url, {'title': 'Neuer Titel'}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)

        delete_resp = self.client.delete(url)
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)
