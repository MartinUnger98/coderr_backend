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

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        user_type = validated_data.pop("type")
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, username=user.username, type=user_type)
        return user

    def to_representation(self, instance):
        token, created = Token.objects.get_or_create(user=instance)
        return {
            "token": token.key,
            "username": instance.username,
            "email": instance.email,
            "user_id": instance.id
        }
