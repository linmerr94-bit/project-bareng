from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class BrandProfile(models.Model):
    """
    Model untuk profil brand/seller yang terdaftar di platform.
    Sesuai dengan SRS REQ-F001: Kelola Brand oleh Admin
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Menunggu Persetujuan'),
        ('APPROVED', 'Disetujui'),
        ('SUSPENDED', 'Ditangguhkan'),
    ]
    
    # Relasi ke user (seller/brand owner)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brand_profile',
        help_text="Pemilik/Admin dari brand ini"
    )
    
    # Nama brand
    brand_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nama unik dari brand/toko"
    )
    
    # Dokumen verifikasi (NIB atau KTP)
    nib_or_ktp = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nomor Induk Berusaha (NIB) atau Nomor KTP untuk verifikasi"
    )
    
    # Rating brand
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Rating brand dari customer (0.0 - 5.0)"
    )
    
    # Status persetujuan brand
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Status persetujuan brand oleh admin"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal pendaftaran brand"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal pembaruan terakhir"
    )
    
    class Meta:
        verbose_name = "Brand Profile"
        verbose_name_plural = "Brand Profiles"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.brand_name} ({self.get_status_display()})"
