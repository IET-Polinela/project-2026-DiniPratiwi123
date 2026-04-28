from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_admin',
        'is_member',
        'is_staff',
        'is_superuser',
    )

    list_filter = (
        'is_admin',
        'is_member',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Role Aplikasi', {'fields': ('is_admin', 'is_member')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Aplikasi', {'fields': ('is_admin', 'is_member')}),
    )