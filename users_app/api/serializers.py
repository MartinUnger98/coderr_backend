from rest_framework import serializers
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles user creation along with the associated user profile.
    Ensures password confirmation and assigns profile type.
    """
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=[("customer", "Customer"), ("business", "Business")])

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):
        """
        Save the new user and their profile.

        Raises:
            ValidationError: If passwords do not match.

        Returns:
            User: The created user instance.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'password dont match'})

        account = self._create_user()
        self._create_profile(account)
        return account

    def _create_user(self):
        """
        Create the User instance.

        Returns:
            User: The created user.
        """
        return User.objects.create_user(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            password=self.validated_data['password']
        )

    def _create_profile(self, account):
        """
        Create a UserProfile for the given user.

        Args:
            account (User): The user to associate with the profile.
        """
        UserProfile.objects.create(
            user=account,
            username=account.username,
            type=self.validated_data["type"]
        )


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing business user profiles.
    """

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type"
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing customer user profiles.
    """

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file", "uploaded_at", "type"
        ]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed user profile information,
    including email and account creation date.
    """
    email = serializers.EmailField(source="user.email", required=False)
    created_at = serializers.DateTimeField(
        source="user.date_joined", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user", "username", "first_name", "last_name", "file", "location",
            "tel", "description", "working_hours", "type", "email", "created_at"
        ]
        
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        email = user_data.get('email')

        if email:
            instance.user.email = email
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading a profile file.
    """

    class Meta:
        model = UserProfile
        fields = ['file', 'uploaded_at']
