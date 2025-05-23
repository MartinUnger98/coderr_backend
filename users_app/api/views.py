from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from users_app.models import UserProfile
from .serializers import BusinessProfileListSerializer, CustomerProfileListSerializer, UserProfileDetailSerializer, FileUploadSerializer
from rest_framework.permissions import IsAuthenticated
from.permissions import IsOwnerOrReadOnly

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
        else:
            data=serializer.errors
            
        return Response(data)
    
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
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
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        user_id = self.kwargs["pk"]
        return UserProfile.objects.get(user__id=user_id)

class BusinessProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type="business")
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

class CustomerProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type="customer")
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    
class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)