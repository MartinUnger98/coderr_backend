from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class TestOrderCRUD(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz_crud', password='1234')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='biz_crud', type='business')
        self.business_token = Token.objects.create(user=self.business_user)
        self.business_auth = {
            'HTTP_AUTHORIZATION': f'Token {self.business_token.key}'}

        self.customer_user = User.objects.create_user(
            username='cust_crud', password='1234')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='cust_crud', type='customer')
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

    def test_create_order(self):
        response = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], self.offer_detail.title)

    def test_list_orders_as_customer(self):
        self.client.post('/api/orders/', self.order_payload,
                         **self.customer_auth)
        response = self.client.get('/api/orders/', **self.customer_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_order_missing_offer_detail_id(self):
        response = self.client.post('/api/orders/', {}, **self.customer_auth)
        self.assertEqual(response.status_code, 400)
        self.assertIn('offer_detail_id', response.data)
        
    def test_create_order_invalid_offer_detail_id_type(self):
        response = self.client.post('/api/orders/', {'offer_detail_id': 'abc'}, **self.customer_auth)
        self.assertEqual(response.status_code, 400)
        self.assertIn('offer_detail_id', response.data)

    def test_create_order_nonexistent_offer_detail_id(self):
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': 999}, **self.customer_auth)
        self.assertEqual(response.status_code, 400)

    def test_admin_can_delete_order(self):
        response = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth)
        order_id = response.data['id']

        admin_user = User.objects.create_superuser(
            'admin', 'admin@mail.com', 'adminpass')
        Token.objects.create(user=admin_user)
        admin_auth = {
            'HTTP_AUTHORIZATION': f'Token {admin_user.auth_token.key}'}

        response = self.client.delete(
            f'/api/orders/{order_id}/delete/', **admin_auth)
        self.assertEqual(response.status_code, 204)

    def test_non_admin_cannot_delete_order(self):
        response = self.client.post(
            '/api/orders/', self.order_payload, **self.customer_auth)
        order_id = response.data['id']

        response = self.client.delete(
            f'/api/orders/{order_id}/delete/', **self.customer_auth)
        self.assertEqual(response.status_code, 403)
