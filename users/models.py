from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for the custom user model with role-aware create helpers."""

    use_in_migrations = True

    def _create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('role') is None:
            extra_fields['role'] = 'customer'
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User Model untuk platform B2B2C VOLTA.
    Extends AbstractUser dengan field tambahan untuk role-based access control.
    """
    
    # Pilihan role pengguna
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('brand', 'Brand/Vendor'),
        ('customer', 'Customer'),
    )
    
    # Override primary key dengan nama custom
    user_id = models.AutoField(primary_key=True)
    
    # Field untuk role
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        help_text="Role pengguna dalam sistem (admin, brand, atau customer)"
    )
    
    # Field untuk nama lengkap
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nama lengkap pengguna"
    )
    
    # Field untuk nomor telepon
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="Nomor telepon kontak pengguna"
    )
    
    # Field untuk alamat
    address_street = models.TextField(
        blank=True,
        null=True,
        help_text="Jalan dan nomor rumah"
    )
    
    address_city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Kota/Kabupaten"
    )
    
    address_province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Provinsi"
    )
    
    address_postal_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Kode pos"
    )
    
    # Override default is_active
    is_active = models.BooleanField(
        default=True,
        help_text="Menunjukkan apakah user ini aktif atau tidak"
    )
    
    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal dan waktu user dibuat"
    )

    objects = UserManager()
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal dan waktu user terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def toko(self):
        """
        Alias ke profile toko/vendor yang dimiliki user ini.
        Digunakan untuk akses tenant-aware store isolation.
        """
        return getattr(self, 'brand_vendor', None)
    
    def get_role_display(self):
        """Return display name untuk role"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
