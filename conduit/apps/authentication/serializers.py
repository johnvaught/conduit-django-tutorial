from rest_framework import serializers
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializes a registration request and creates a new user.
    """
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'handle', 'email', 'password', 'refresh_token', 'access_token']
