from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token

class OfferDetailAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='biz', password='testpass')
        UserProfile.objects.create(user=self.user, username='biz', type='business')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

        self.offer = Offer.objects.create(user=self.user, title='Flyer Design', description='Top Design')
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=5,
            delivery_time_in_days=7,
            price=300,
            features=["Flyer", "Poster"],
            offer_type='premium'
        )

    def test_get_detail_authenticated(self):
        url = reverse('offer-details', kwargs={'id': self.detail.id})
        response = self.client.get(url, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail.id)
        self.assertEqual(response.data['title'], 'Premium')

    def test_get_detail_unauthenticated(self):
        url = reverse('offer-details', kwargs={'id': self.detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_detail(self):
        url = reverse('offer-details', kwargs={'id': 9999})
        response = self.client.get(url, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
