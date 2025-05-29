from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile

class TestReviewPermissions(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz_perm', password='1234')
        self.business_profile = UserProfile.objects.create(user=self.business_user, username='biz_perm', type='business')

        self.customer_user = User.objects.create_user(username='cust_perm', password='1234')
        self.customer_profile = UserProfile.objects.create(user=self.customer_user, username='cust_perm', type='customer')

        self.token = Token.objects.create(user=self.business_user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

        self.payload = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Test"
        }

    def test_business_user_cannot_create_review(self):
        response = self.client.post('/api/reviews/', self.payload, **self.auth)
        self.assertEqual(response.status_code, 403)
