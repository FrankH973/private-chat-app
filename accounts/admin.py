# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserInvitation, BiometricToken

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_email_verified', 'is_staff', 'created_at']
    list_filter = ['is_email_verified', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'username']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'avatar', 'is_email_verified', 'public_key')
        }),
    )

@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'invited_by', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email', 'invited_by__email']
    readonly_fields = ['token', 'created_at']

@admin.register(BiometricToken)
class BiometricTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'is_active', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'device_name', 'device_id']
    readonly_fields = ['created_at', 'last_used']