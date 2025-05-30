from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from users_app.models import UserProfile
from reviews_app.models import Review


class TestReviewUpdateDelete(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz_owner', password='1234')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user, username='biz_owner', type='business')

        self.customer_user = User.objects.create_user(
            username='cust_edit', password='1234')
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user, username='cust_edit', type='customer')

        self.token = Token.objects.create(user=self.customer_user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Gut"
        )

    def test_update_review(self):
        response = self.client.patch(f'/api/reviews/{self.review.id}/', {
            "rating": 3,
            "description": "Geändert"
        }, **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating"], 3)

    def test_delete_review(self):
        response = self.client.delete(
            f'/api/reviews/{self.review.id}/', **self.auth)
        self.assertEqual(response.status_code, 204)
