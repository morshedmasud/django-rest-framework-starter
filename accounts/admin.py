from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from . import models

# Register your models here.
user = get_user_model()


class AccessTokensAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'access_token', 'created_at', 'expired_at']


class RefreshTokensAdmin(admin.ModelAdmin):
    list_display = ['id', 'refresh_token', 'access_token_id', 'created_at', 'expired_at']


# admin.site.unregister(Group)
admin.site.register(user)
admin.site.register(models.Role)