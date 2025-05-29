from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile
from orders_app.models import Order


class TestOrderCounts(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz_count', password='1234')
        self.business_profile = UserProfile.objects.create(user=self.business_user, username='biz_count', type='business')
        self.business_token = Token.objects.create(user=self.business_user)
        self.business_auth = {'HTTP_AUTHORIZATION': f'Token {self.business_token.key}'}

        self.customer_user = User.objects.create_user(username='cust_count', password='1234')
        self.customer_profile = UserProfile.objects.create(user=self.customer_user, username='cust_count', type='customer')
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.customer_auth = {'HTTP_AUTHORIZATION': f'Token {self.customer_token.key}'}

        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Test',
            revisions=2,
            delivery_time_in_days=3,
            price=100,
            features=['f1'],
            offer_type='basic',
            status='in_progress'
        )

        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Test 2',
            revisions=2,
            delivery_time_in_days=3,
            price=100,
            features=['f1'],
            offer_type='basic',
            status='completed'
        )

    def test_in_progress_count(self):
        url = f'/api/order-count/{self.business_user.id}/'
        response = self.client.get(url, **self.business_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_count(self):
        url = f'/api/completed-order-count/{self.business_user.id}/'
        response = self.client.get(url, **self.business_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_404_on_nonexistent_user(self):
        url = f'/api/order-count/99999/'
        response = self.client.get(url, **self.business_auth)
        self.assertEqual(response.status_code, 404)
