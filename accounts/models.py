from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, email, full_name, password=None):
        if not email:
            raise ValueError('User must have email')

        email = email.lower()
        full_name = full_name.title()

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user_social(self, email=None, full_name=None, provider=None, social_id=None):
        if not provider and social_id:
            raise ValueError('Provider and social id is missing')

        email = email.lower()
        full_name = full_name.title()

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            provider=provider,
            social_id=social_id
        )
        user.is_verified = True

        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email=email,
            full_name=full_name if full_name else email,
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)

        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'twitter': 'twitter', 'email': 'email'}


class User(AbstractBaseUser):

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'
    STATUS = [
        (ACTIVE, _('Active user')),
        (INACTIVE, _('User Inactive')),
        (DELETED, _('Soft Delete user')),
    ]

    email = models.EmailField(max_length=200, unique=True, null=True, blank=True, verbose_name='email')
    full_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='Full Name')
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='user_images/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    verify_code = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    auth_id = models.TextField(null=True, blank=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    status = models.CharField(max_length=32, choices=STATUS, default=ACTIVE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    class Meta:
        verbose_name_plural = 'users'

    def get_user_info(self):
        return {
            'user_id': self.id,
            'email': self.email,
            'full_name': self.full_name
        }

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
