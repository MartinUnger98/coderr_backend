from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile
from reviews_app.models import Review


class TestReviewCRUD(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz_crud', password='1234')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='biz_crud', type='business')

        self.customer_user = User.objects.create_user(
            username='cust_crud', password='1234')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='cust_crud', type='customer')

        self.token = Token.objects.create(user=self.customer_user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

        self.payload = {
            "business_user": self.business_user.id,
            "rating": 5,
            "description": "Sehr gut"
        }

    def test_create_review(self):
        response = self.client.post('/api/reviews/', self.payload, **self.auth)
        self.assertEqual(response.status_code, 201)

    def test_list_reviews(self):
        self.client.post('/api/reviews/', self.payload, **self.auth)
        response = self.client.get('/api/reviews/', **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
