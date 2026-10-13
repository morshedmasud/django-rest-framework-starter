from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('verify-email', views.VerifyEmail.as_view(), name='verify-email'),
    path('resend-verification', views.ResendVerificationEmail.as_view(), name='resend-verification'),
    path('login', views.LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout', views.LogoutView.as_view(), name='logout'),

    path('request-reset-password', views.ResetPasswordWithEmail.as_view(), name='request-reset-password'),
    path('password-reset/<uidb64>/<token>', views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', views.SetNewPasswordAPIView.as_view(), name='password-reset-complete'),

    path('me', views.MeAPIView.as_view(), name='me'),
    path('users', views.UserListAPIView.as_view(), name='all-users'),
    path('<int:id>', views.UserDetailsAPIView.as_view(), name='single-user'),
]
