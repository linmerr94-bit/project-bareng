from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin untuk platform B2B2C VOLTA.
    Extends dari UserAdmin bawaan Django dengan customization untuk fields tambahan.
    """
    
    # Kolom yang ditampilkan di tampilan tabel list user
    list_display = (
        'user_id',
        'username',
        'email',
        'full_name',
        'role',
        'phone',
        'is_active',
        'created_at',
    )
    
    # Filter yang tersedia di sidebar
    list_filter = ('role', 'is_active', 'created_at')
    
    # Field yang bisa di-search
    search_fields = ('username', 'email', 'full_name', 'phone')
    
    # Pengaturan fieldsets untuk tampilan detail user
    fieldsets = (
        # Informasi Login & Identitas Dasar
        (_('Login Information'), {
            'fields': ('username', 'password')
        }),
        
        # Informasi Personal
        (_('Personal Information'), {
            'fields': ('email', 'full_name', 'phone')
        }),
        
        # Informasi Role (Custom untuk VOLTA)
        (_('VOLTA Role & Status'), {
            'fields': ('role', 'is_active'),
            'description': 'Kelola role pengguna (admin, brand, atau customer) dan status akun.'
        }),
        
        # Permissions dan Status Django
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        
        # Timestamps (Read-only)
        (_('Important Dates'), {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets untuk tampilan create (add) user baru
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Personal Information'), {
            'classes': ('wide',),
            'fields': ('full_name', 'phone', 'role'),
        }),
    )
    
    # Field yang read-only (tidak bisa diedit)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    # Urutan field di list view
    ordering = ('-created_at',)
