from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from import_export.admin import ImportExportMixin

from . import models


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = models.CustomUser
        fields = ('email', 'full_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.CustomUser
        fields = '__all__'


@admin.register(models.CustomUser)
class UserModelAdmin(ImportExportMixin, UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'full_name', 'auth_provider', 'is_verified', 'is_staff', 'is_active', 'deleted')
    list_filter = ('auth_provider', 'is_verified', 'is_staff', 'is_superuser', 'is_active', 'deleted')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('full_name', 'phone', 'photo', 'address')}),
        ('Status', {'fields': ('is_verified', 'status', 'deleted', 'auth_provider', 'auth_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'usable_password', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        # Show soft-deleted users too.
        return self.model.all_objects.all()


@admin.register(models.ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'message')
    list_filter = ('level',)
    search_fields = ('message',)
    readonly_fields = ('timestamp', 'level', 'message', 'details')
