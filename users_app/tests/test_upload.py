from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status


class UploadTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='uploaduser', password='uploadpass')
        self.profile = UserProfile.objects.create(
            user=self.user, username='uploaduser', type='customer')
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('file-upload')

    def test_file_upload_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        file = SimpleUploadedFile(
            "testfile.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(self.url, {"file": file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("file", response.data)
