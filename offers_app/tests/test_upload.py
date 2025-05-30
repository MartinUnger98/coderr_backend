from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from ..models import Offer
from users_app.models import UserProfile


class FileUploadTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='biz', password='testpass')
        self.profile = UserProfile.objects.create(
            user=self.user, username='biz', type='business')
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('file-upload')

    def test_upload_file_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        file = SimpleUploadedFile(
            "testfile.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(self.url, {"file": file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("file", response.data)

    def test_upload_file_unauthenticated(self):
        file = SimpleUploadedFile(
            "test.jpg", b"testcontent", content_type="image/jpeg")
        response = self.client.post(
            self.url, {'image': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
