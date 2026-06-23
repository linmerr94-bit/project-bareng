from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from brands.models import BrandProfile


class Category(models.Model):
    """
    Model untuk kategori produk elektronik.
    Misalnya: Smartphone, TV, AC, Laptop, dll
    """
    
    # Nama kategori
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nama kategori produk (e.g., Smartphone, TV, AC)"
    )
    
    # Deskripsi kategori
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi detail kategori produk"
    )
    
    # Status aktif/tidak
    is_active = models.BooleanField(
        default=True,
        help_text="Kategori aktif atau tidak"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal pembuatan kategori"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal pembaruan terakhir"
    )
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model untuk produk yang dijual oleh brand.
    Sesuai dengan SRS REQ-F009 (Dual Pricing) dan REQ-F010 (MOQ dan Stock)
    """
    
    # Relasi ke brand/seller
    brand = models.ForeignKey(
        BrandProfile,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Brand/Seller yang menjual produk ini"
    )
    
    # Relasi ke kategori produk
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        help_text="Kategori produk"
    )
    
    # Nama produk
    name = models.CharField(
        max_length=255,
        help_text="Nama produk"
    )
    
    # SKU (Stock Keeping Unit)
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Kode SKU unik untuk produk"
    )
    
    # Deskripsi produk
    description = models.TextField(
        help_text="Deskripsi detail produk"
    )
    
    # REQ-F009: Harga B2C (Business to Consumer / Eceran)
    price_b2c = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Harga eceran untuk konsumen individual"
    )
    
    # REQ-F009: Harga B2B (Business to Business / Grosir)
    price_b2b = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Harga grosir untuk pembeli dalam jumlah besar"
    )
    
    # REQ-F010: MOQ B2B (Minimum Order Quantity untuk pesanan grosir)
    moq_b2b = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Jumlah minimum pemesanan untuk harga B2B"
    )
    
    # REQ-F010: Stok produk
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Jumlah stok produk yang tersedia"
    )
    
    # Status produk
    is_active = models.BooleanField(
        default=True,
        help_text="Produk aktif atau tidak"
    )
    
    # Rating produk
    rating = models.FloatField(
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ],
        help_text="Rating produk dari customer (0.0 - 5.0)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal produk dibuat"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal pembaruan terakhir"
    )
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['sku']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price_b2b__lte=models.F('price_b2c')),
                name='price_b2b_must_be_less_than_or_equal_price_b2c'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku}) - {self.brand.brand_name}"
    
    def get_price_for_quantity(self, quantity):
        """
        Menentukan harga berdasarkan jumlah pemesanan.
        
        Args:
            quantity (int): Jumlah yang dipesan
            
        Returns:
            decimal: Harga per unit sesuai quantity
        """
        if quantity >= self.moq_b2b:
            return self.price_b2b
        return self.price_b2c
