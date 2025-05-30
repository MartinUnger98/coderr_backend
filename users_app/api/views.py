from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from users_app.models import UserProfile
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    UserProfileDetailSerializer,
    FileUploadSerializer
)
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly


class RegistrationView(APIView):
    """
    API endpoint for user registration.

    Allows anyone to register a new user and returns an authentication token upon success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests to register a new user.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            return self._build_success_response(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _build_success_response(self, serializer):
        """
        Helper method to save the user and return a token response.
        """
        saved_account = serializer.save()
        token, _ = Token.objects.get_or_create(user=saved_account)
        return Response({
            'token': token.key,
            'username': saved_account.username,
            'email': saved_account.email,
            'user_id': saved_account.id
        })


class CustomLoginView(ObtainAuthToken):
    """
    Custom login view that returns token and user info upon successful authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for login.
        """
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        user = token.user
        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        })


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve or update a user's profile.

    Only authenticated users can access or update their own profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """
        Get the profile object based on the user ID from the URL.
        """
        user_id = self.kwargs["pk"]
        obj = UserProfile.objects.get(user__id=user_id)
        self.check_object_permissions(self.request, obj)
        return obj


class BusinessProfileListView(generics.ListAPIView):
    """
    View to list all business user profiles.

    Accessible to authenticated users.
    """
    queryset = UserProfile.objects.filter(type="business")
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """
    View to list all customer user profiles.

    Accessible to authenticated users.
    """
    queryset = UserProfile.objects.filter(type="customer")
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]


class FileUploadView(APIView):
    """
    View to handle profile image file uploads.

    Only authenticated users can upload files for their own profile.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handles POST request to upload a file to the user's profile.
        """
        profile = UserProfile.objects.get(user=request.user)
        serializer = FileUploadSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
