from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile
from offers_app.models import Offer, OfferDetail


class TestOrderPermissions(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz_perm', password='1234')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='biz_perm', type='business')
        self.business_token = Token.objects.create(user=self.business_user)
        self.business_auth = {
            'HTTP_AUTHORIZATION': f'Token {self.business_token.key}'}

        self.customer_user = User.objects.create_user(
            username='cust_perm', password='1234')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='cust_perm', type='customer')
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.customer_auth = {
            'HTTP_AUTHORIZATION': f'Token {self.customer_token.key}'}

        self.offer = Offer.objects.create(
            user=self.business_user, title="Design", description="Desc")
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=3,
            delivery_time_in_days=5,
            price=99.99,
            features=["Logo"],
            offer_type="basic"
        )

        self.order_payload = {"offer_detail_id": self.offer_detail.id}

    def test_customer_can_create_order(self):
        response = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth)
        self.assertEqual(response.status_code, 201)

    def test_business_user_cannot_create_order(self):
        response = self.client.post(
            '/api/orders/', self.order_payload, **self.business_auth)
        self.assertEqual(response.status_code, 403)

    def test_business_user_can_update_status(self):
        order = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth).data
        order_id = order['id']
        response = self.client.patch(
            f'/api/orders/{order_id}/',
            data={'status': 'completed'},
            format='json',
            **self.business_auth
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'completed')

    def test_customer_cannot_update_status(self):
        order = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth).data
        order_id = order['id']

        response = self.client.patch(
            f'/api/orders/{order_id}/',
            data={'status': 'completed'},
            format='json',
            **self.customer_auth
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_status_rejected(self):
        order = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth).data
        order_id = order['id']

        response = self.client.patch(
            f'/api/orders/{order_id}/',
            data={'status': 'nonsense'},
            format='json',
            **self.business_auth
        )
        self.assertEqual(response.status_code, 400)
