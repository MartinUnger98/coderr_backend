from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token

class OfferFilteringTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='testpass')
        self.user2 = User.objects.create_user(username='u2', password='testpass')
        UserProfile.objects.create(user=self.user1, username='u1', type='business')
        UserProfile.objects.create(user=self.user2, username='u2', type='business')
        Token.objects.create(user=self.user1)
        Token.objects.create(user=self.user2)

        self.offer1 = Offer.objects.create(user=self.user1, title='Logo Design', description='Professionell')
        self.offer2 = Offer.objects.create(user=self.user2, title='Flyer Design', description='Modern')

        OfferDetail.objects.create(offer=self.offer1, title='Basic', revisions=1, delivery_time_in_days=3, price=50, features=[], offer_type='basic')
        OfferDetail.objects.create(offer=self.offer1, title='Premium', revisions=5, delivery_time_in_days=5, price=150, features=[], offer_type='premium')

        OfferDetail.objects.create(offer=self.offer2, title='Basic', revisions=1, delivery_time_in_days=10, price=200, features=[], offer_type='basic')

    def test_filter_by_creator_id(self):
        url = reverse('offers-list') + f"?creator_id={self.user1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user1.id)

    def test_filter_by_min_price(self):
        url = reverse('offers-list') + "?min_price=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(float(o['min_price']) >= 100 for o in response.data['results']))

    def test_filter_by_max_delivery_time(self):
        url = reverse('offers-list') + "?max_delivery_time=5"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(o['min_delivery_time'] <= 5 for o in response.data['results']))

    def test_ordering_by_min_price(self):
        url = reverse('offers-list') + "?ordering=min_price"
        response = self.client.get(url)
        prices = [float(o['min_price']) for o in response.data['results']]
        self.assertEqual(prices, sorted(prices))

    def test_search_in_title_and_description(self):
        url = reverse('offers-list') + "?search=Flyer"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Flyer" in o['title'] for o in response.data['results']))
