from rest_framework import serializers
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=[("customer", "Customer"), ("business", "Business")])

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'password dont match'})
        
        account = User.objects.create_user(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            password=pw
        )
        UserProfile.objects.create(
            user=account,
            username=account.username,
            type=self.validated_data["type"]
        )
        return account
    
class BusinessProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type"
        ]

class CustomerProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file", "uploaded_at", "type"
        ]
        
class UserProfileDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    created_at = serializers.DateTimeField(source="user.date_joined", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file", "location",
            "tel", "description", "working_hours", "type", "email", "created_at"
        ]
        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['file', 'uploaded_at']
