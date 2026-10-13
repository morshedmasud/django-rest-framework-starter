from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import signing
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, views
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from services.customPermission import IsSelfOrAdmin

from .serializers import (
    LoginResponseSerializer, LoginSerializer, RefreshTokenSerializer, RegisterSerializer,
    ResetPasswordWithEmailSerializer, SetNewPasswordSerializer, UsersSerializer,
    get_user_from_reset_token,
)
from .utils import Util

EMAIL_VERIFICATION_SALT = 'accounts.email-verification'


def make_email_verification_token(user):
    return signing.dumps({'user_id': user.id}, salt=EMAIL_VERIFICATION_SALT)


def send_verification_email(request, user):
    token = make_email_verification_token(user)
    abs_url = request.build_absolute_uri(reverse('verify-email')) + f'?token={token}'
    Util.send_email({
        'to_email': user.email,
        'email_subject': 'Verify your email',
        'email_body': f'Hi {user.full_name or user.email},\nUse the link below to verify your email:\n{abs_url}',
    })


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'auth'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(request, user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    permission_classes = (permissions.AllowAny,)

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Token from the verification email', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        try:
            payload = signing.loads(
                request.GET.get('token', ''), salt=EMAIL_VERIFICATION_SALT,
                max_age=settings.EMAIL_VERIFICATION_MAX_AGE)
            user = CustomUser.objects.get(id=payload['user_id'])
        except (signing.BadSignature, CustomUser.DoesNotExist, KeyError, TypeError):
            raise ValidationError({'token': 'Invalid or expired token.'})
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified', 'updated_at'])
        return Response({'message': 'Email successfully verified.'}, status=status.HTTP_200_OK)


class ResendVerificationEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordWithEmailSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'auth'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.active().filter(
            email__iexact=serializer.validated_data['email'], is_verified=False).first()
        if user:
            send_verification_email(request, user)
        return Response({'message': 'If the account exists and is unverified, a verification email has been sent.'})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'auth'

    @swagger_auto_schema(
        operation_summary="Authenticate and login a user",
        responses={200: LoginResponseSerializer, 401: "Incorrect credentials"},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request,
            email=serializer.validated_data['email'].lower(),
            password=serializer.validated_data['password'],
        )
        if user is None:
            raise AuthenticationFailed('Incorrect email or password.')
        if settings.REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
            raise AuthenticationFailed('Email is not verified.')
        if user.deleted:
            user.restore()
        return Response({'user': UsersSerializer(user).data, 'tokens': user.tokens()}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data['refresh']).blacklist()
        except TokenError:
            raise ValidationError({'refresh': 'Invalid or expired token.'})
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordWithEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordWithEmailSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'auth'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.active().filter(email__iexact=serializer.validated_data['email']).first()
        if user and user.has_usable_password():
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            abs_url = request.build_absolute_uri(
                reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token}))
            Util.send_email({
                'to_email': user.email,
                'email_subject': 'Reset your password',
                'email_body': f'Hi,\nUse the link below to reset your password:\n{abs_url}',
            })

        # Same response either way, so the endpoint can't be used to discover registered emails.
        return Response({'message': 'If an account with that email exists, we have sent a password reset link.'},
                        status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token):
        get_user_from_reset_token(uidb64, token)
        return Response({'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'auth'

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset success.'}, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListAPIView):
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        return CustomUser.objects.active().order_by('-created_at')


class UserDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsSelfOrAdmin)
    lookup_field = 'id'

    def get_queryset(self):
        return CustomUser.objects.active()


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UsersSerializer

    def get_object(self):
        return self.request.user
