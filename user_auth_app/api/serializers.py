from rest_framework import serializers
from user_auth_app.models import CustomUser
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'password', 'confirm_password', 'emblem', 'color']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise AuthenticationFailed('Passwords do not match.')
        return data
    
    def validate_email(self, value):
        """
        Überprüft, ob die E-Mail bereits verwendet wird.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("email is already in use.")
        return value

    def validate_username(self, value):
        """
        Überprüft, ob der Benutzername bereits verwendet wird.
        """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("username is already taken.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['email'] = validated_data['email'].lower()
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'emblem', 'color']


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        if not email or not password:
            raise AuthenticationFailed("Must include 'email' and 'password'.")

        user = authenticate(username=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("This account is inactive.")

        attrs['user'] = user
        return attrs