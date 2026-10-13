from rest_framework import serializers

from . import facebook, google
from .register import register_social_user


class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)
        if not user_data or 'id' not in user_data:
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')

        return register_social_user(
            provider='facebook',
            user_id=user_data['id'],
            email=user_data.get('email'),
            name=user_data.get('name'),
        )


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        if not user_data or 'sub' not in user_data:
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')
        if not user_data.get('email_verified'):
            raise serializers.ValidationError('Your Google email address is not verified.')

        return register_social_user(
            provider='google',
            user_id=user_data['sub'],
            email=user_data.get('email'),
            name=user_data.get('name'),
        )
