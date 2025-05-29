from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review

class TestBaseInfoEndpoint(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz_user', password='1234')
        self.business_profile = UserProfile.objects.create(user=self.business_user, username='biz_user', type='business')

        self.customer_user = User.objects.create_user(username='cust_user', password='1234')
        self.customer_profile = UserProfile.objects.create(user=self.customer_user, username='cust_user', type='customer')

        self.customer_user2 = User.objects.create_user(username='cust_user2', password='1234')
        self.customer_profile2 = UserProfile.objects.create(user=self.customer_user2, username='cust_user2', type='customer')

        for i in range(3):
            Offer.objects.create(user=self.business_user, title=f"Angebot {i}", description="Testbeschreibung")

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
            description="Gut!"
        )

    def test_base_info_data(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['business_profile_count'], 1)
        self.assertEqual(response.data['offer_count'], 3)
        self.assertEqual(response.data['average_rating'], 4.5)
