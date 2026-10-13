from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'password']

    def validate_email(self, value):
        value = value.lower()
        if CustomUser.all_objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        validate_password(attrs['password'], CustomUser(email=attrs['email'], full_name=attrs.get('full_name')))
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class TokensSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResetPasswordWithEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


def get_user_from_reset_token(uidb64, token):
    """Return the user for a valid password reset link, or raise AuthenticationFailed."""
    try:
        user = CustomUser.objects.get(id=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is None or not PasswordResetTokenGenerator().check_token(user, token):
        raise AuthenticationFailed('The reset link is invalid or has expired, please request a new one.')
    return user


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = get_user_from_reset_token(attrs['uidb64'], attrs['token'])
        validate_password(attrs['password'], user)
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'phone', 'photo', 'address',
                  'is_verified', 'status', 'created_at']
        read_only_fields = ['id', 'email', 'is_verified', 'status', 'created_at']


class LoginResponseSerializer(serializers.Serializer):
    user = UsersSerializer()
    tokens = TokensSerializer()
