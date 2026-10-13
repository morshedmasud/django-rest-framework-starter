from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from uuid import uuid4


class UserManager(BaseUserManager):

    def create_user(self, email, full_name=None, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have email')

        user = self.model(
            email=self.normalize_email(email).lower(),
            full_name=full_name.title() if full_name else full_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user_social(self, email, full_name=None, provider=None, social_id=None):
        if not provider or not social_id:
            raise ValueError('Provider and social id are required')

        user = self.model(
            email=self.normalize_email(email).lower(),
            full_name=full_name.title() if full_name else full_name,
            auth_provider=provider,
            auth_id=social_id,
            is_verified=True,
        )
        # Social users sign in through their provider only, never with a password.
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name=None, password=None, **extra_fields):
        extra_fields.update(is_admin=True, is_staff=True, is_superuser=True, is_verified=True)
        return self.create_user(
            email=email,
            full_name=full_name if full_name else email,
            password=password,
            **extra_fields
        )

    def active(self):
        """Users that have not been soft deleted."""
        return self.get_queryset().filter(deleted=False)


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'twitter': 'twitter', 'email': 'email'}


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'
    STATUS = [
        (ACTIVE, _('Active user')),
        (INACTIVE, _('User Inactive')),
        (DELETED, _('Soft Delete user')),
    ]

    email = models.EmailField(max_length=200, unique=True, verbose_name='email')
    full_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='Full Name')
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='user_images/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    auth_id = models.TextField(null=True, blank=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    deleted = models.BooleanField(default=False)

    status = models.CharField(max_length=32, choices=STATUS, default=ACTIVE)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    all_objects = models.Manager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.full_name

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

    def delete(self, using=None, keep_parents=False):
        """Soft delete. Logging in again restores the account. Use hard_delete() to remove the row."""
        self.deleted = True
        self.status = self.DELETED
        self.save(update_fields=['deleted', 'status', 'updated_at'])

    def restore(self):
        self.deleted = False
        self.status = self.ACTIVE
        self.save(update_fields=['deleted', 'status', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


class ModelManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(Q(active=False) | Q(deleted=True))


class BaseModel(models.Model):
    """Abstract base with a public UUID, timestamps and soft delete. `objects` hides deleted rows."""
    objects = ModelManager()
    all_objects = models.Manager()
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.active = False
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True


class ErrorLog(models.Model):
    level = models.CharField(max_length=50)
    message = models.TextField()
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.level}] {self.timestamp}: {self.message[:50]}"
