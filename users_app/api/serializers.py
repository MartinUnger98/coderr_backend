from rest_framework import serializers
from django.contrib.auth.models import User
from users_app.models import UserProfile
from rest_framework.authtoken.models import Token


from rest_framework import serializers
from django.contrib.auth.models import User
from users_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates and creates a new User along with a related UserProfile.
    """
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=[("customer", "Customer"), ("business", "Business")])

    username = serializers.CharField(
        required=True,
        write_only=False
    )
    email = serializers.EmailField(
        required=True,
        write_only=False
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_username(self, value):
        """
        Ensure the username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit diesem Benutzernamen existiert bereits.")
        return value

    def validate_email(self, value):
        """
        Ensure the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.")
        return value

    def validate(self, data):
        """
        Ensure the password and repeated password match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Die Passwörter stimmen nicht überein.'})
        return data

    def save(self):
        """
        Create the User and associated UserProfile instance.
        """
        user = User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password']
        )
        UserProfile.objects.create(
            user=user,
            username=user.username,
            type=self.validated_data["type"]
        )
        return user


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
