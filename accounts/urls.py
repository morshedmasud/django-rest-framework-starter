from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('verify-email', views.VerifyEmail.as_view(), name='verify-email'),
    path('login', views.LoginApiView.as_view(), name='login'),

    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('request-reset-password', views.ResetPasswordWithEmail.as_view(), name='request-reset-password'),
    path('password-reset/<uidb64>/<token>', views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', views.SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    
    path('me', views.MeAPIView.as_view(), name='me'),
    path('users', views.UserListAPIView.as_view(), name='all-users'),
    path('<int:id>', views.UserDetailsAPIView.as_view(), name="single-user"),
]
