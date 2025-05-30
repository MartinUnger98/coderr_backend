from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404



class OfferCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='biz', password='testpass')
        self.profile = UserProfile.objects.create(
            user=self.user, username='biz', type='business')
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

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

    def test_create_offer(self):
        url = reverse('offers-list')
        res = self.client.post(url, self.offer_payload,
                               format='json', **self.auth_header)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_get_offers(self):
        self.client.post(reverse('offers-list'),
                         self.offer_payload, format='json', **self.auth_header)
        res = self.client.get(reverse('offers-list'), **self.auth_header)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data['results']), 1)

    def test_get_offer_detail(self):
        res = self.client.post(
            reverse('offers-list'), self.offer_payload, format='json', **self.auth_header)
        offer_id = res.data['id']
        url = reverse('offer-detail-update-delete', kwargs={'id': offer_id})
        detail_res = self.client.get(url, **self.auth_header)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.data['id'], offer_id)

    def test_patch_offer_updates_offer_detail(self):
        res = self.client.post(reverse('offers-list'), self.offer_payload, format='json', **self.auth_header)
        url = reverse('offer-detail-update-delete', kwargs={'id': res.data['id']})
        patch_data = {
            "title": "Updated Grafikdesign-Paket",
            "details": [{
                "title": "Basic Design Updated",
                "revisions": 3,
                "delivery_time_in_days": 6,
                "price": 120,
                "features": ["Logo Design", "Flyer"],
                "offer_type": "basic"
            }]
        }
        self.client.patch(url, patch_data, format='json', **self.auth_header)
        detail = OfferDetail.objects.get(offer__id=res.data['id'], offer_type='basic')
        self.assertEqual(detail.title, "Basic Design Updated")
        self.assertEqual(detail.revisions, 3)
        self.assertEqual(detail.delivery_time_in_days, 6)
        self.assertEqual(float(detail.price), 120.00)
        self.assertEqual(detail.features, ["Logo Design", "Flyer"])


    def test_delete_offer(self):
        res = self.client.post(
            reverse('offers-list'), self.offer_payload, format='json', **self.auth_header)
        offer_id = res.data['id']
        url = reverse('offer-detail-update-delete', kwargs={'id': offer_id})
        del_res = self.client.delete(url, **self.auth_header)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)
