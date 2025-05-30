from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review

class TestBaseInfoEndpoint(APITestCase):
    def setUp(self):
        self.business_user = self._create_user("biz_user", "business")
        self.customer_user = self._create_user("cust_user", "customer")
        self.customer_user2 = self._create_user("cust_user2", "customer")

        self._create_offers(self.business_user, count=3)
        self._create_reviews()

    def _create_user(self, username, user_type):
        user = User.objects.create_user(username=username, password="1234")
        UserProfile.objects.create(user=user, username=username, type=user_type)
        return user

    def _create_offers(self, user, count):
        for i in range(count):
            Offer.objects.create(user=user, title=f"Angebot {i}", description="Testbeschreibung")

    def _create_reviews(self):
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Sehr gut!"
        )
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user2,
            rating=4,
            description="Gut"
        )

    def test_base_info_data(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['business_profile_count'], 1)
        self.assertEqual(response.data['offer_count'], 3)
        self.assertEqual(response.data['average_rating'], 4.5)
