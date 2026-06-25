from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# ============================================================================
# BRAND MODEL
# ============================================================================

class Brand(models.Model):
    """
    Model untuk profil brand/vendor di platform B2B2C VOLTA.
    Setiap brand terikat pada satu user dengan role 'brand'.
    """
    
    # Pilihan status brand
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    # Override primary key dengan nama custom
    brand_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke User (One-to-One, setiap brand = 1 user)
    user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brand_vendor',
        db_column='user_id',
        help_text="User/vendor yang memiliki brand ini"
    )
    
    # Nama brand
    brand_name = models.CharField(
        max_length=255,
        help_text="Nama brand/vendor"
    )
    
    # Logo brand
    logo = models.ImageField(
        upload_to='brands/logos/',
        blank=True,
        null=True,
        help_text="Logo brand (rekomendasi: PNG dengan background transparan)"
    )
    
    # Deskripsi brand
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi detail tentang brand/vendor"
    )
    
    # Status persetujuan brand
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status persetujuan brand (pending, approved, rejected, suspended)"
    )
    
    # Tanggal persetujuan
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Tanggal brand disetujui oleh admin"
    )
    
    # Admin yang menyetujui (Foreign Key ke User)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_brands',
        db_column='approved_by',
        help_text="Admin yang menyetujui brand ini"
    )
    
    # NEW: NIB atau KTP (dari BrandProfile)
    nib_or_ktp = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        db_column='nib_or_ktp',
        help_text="Nomor Induk Berusaha (NIB) atau Nomor KTP"
    )
    
    # NEW: Rating brand (aggregated dari Review)
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        db_column='rating',
        help_text="Rating brand dari customer (0.0-5.0)"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal brand didaftar"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal brand terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        db_table = 'brands'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand_name} ({self.get_status_display()})"

    @property
    def nama_toko(self):
        """
        Alias nama toko untuk tampilan yang menggunakan istilah lokal.
        """
        return self.brand_name

    @property
    def is_approved(self):
        """
        Convenience property to check if the brand/shop is approved.
        """
        return self.status == 'approved'


# ============================================================================
# CATEGORY MODEL
# ============================================================================

class Category(models.Model):
    """
    Model untuk kategori produk di platform B2B2C VOLTA.
    Contoh: Electronics, Clothing, Food, dll.
    """
    
    # Override primary key dengan nama custom
    category_id = models.AutoField(primary_key=True)
    
    # Nama kategori (unique)
    category_name = models.CharField(
        max_length=255,
        unique=True,
        default='',
        help_text="Nama kategori produk (harus unik)"
    )
    
    # Deskripsi kategori
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi detail tentang kategori"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal kategori dibuat"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal kategori terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        db_table = 'categories'
        ordering = ['category_name']
        indexes = [
            models.Index(fields=['category_name']),
        ]
    
    def __str__(self):
        return self.category_name


# ============================================================================
# PRODUCT MODEL
# ============================================================================

class Product(models.Model):
    """
    Model untuk produk yang dijual oleh brand di platform B2B2C VOLTA.
    Setiap produk memiliki relasi ke brand dan kategori.
    """
    
    # Override primary key dengan nama custom
    product_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke Brand
    brand_id = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        db_column='brand_id',
        help_text="Brand/vendor penjual produk"
    )
    
    # Foreign Key ke Category
    category_id = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        db_column='category_id',
        help_text="Kategori produk"
    )
    
    # Nama produk
    product_name = models.CharField(
        max_length=255,
        help_text="Nama produk"
    )
    
    # Slug untuk URL (unique)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly identifier untuk produk"
    )
    
    # Deskripsi produk
    description = models.TextField(
        help_text="Deskripsi detail produk"
    )
    
    # Harga produk (Decimal)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Harga jual produk"
    )
    
    # Stok produk (Integer)
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Jumlah stok produk yang tersedia"
    )
    
    # Gambar/foto produk
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Foto/gambar produk"
    )
    
    # Status aktif/tidak
    is_active = models.BooleanField(
        default=True,
        help_text="Status aktif produk (true = aktif, false = non-aktif)"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal produk didaftarkan"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal produk terakhir diperbarui"
    )
    
    # Rating (0-5) untuk produk
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        help_text="Rating produk dari customer (0.00-5.00)"
    )
    
    # Jumlah review/rating yang diterima
    review_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Jumlah review yang diterima produk"
    )
    
    # Status featured/promosi
    is_featured = models.BooleanField(
        default=False,
        help_text="Apakah produk sedang di-featured/promosi"
    )
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['brand_id']),
            models.Index(fields=['category_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.product_name} ({self.brand_id.brand_name})"


# ============================================================================
# CART MODEL
# ============================================================================

class Cart(models.Model):
    """
    Model untuk shopping cart pengguna di platform B2B2C VOLTA.
    Setiap user memiliki satu cart (unique).
    """
    
    # Override primary key dengan nama custom
    cart_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke User (One-to-One, setiap user = 1 cart)
    user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        db_column='user_id',
        help_text="User pemilik cart"
    )
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        db_table = 'carts'
        indexes = [
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Cart of {self.user_id.username}"


# ============================================================================
# CART ITEM MODEL
# ============================================================================

class CartItem(models.Model):
    """
    Model untuk item-item dalam shopping cart.
    Setiap item memiliki relasi ke cart dan produk.
    """
    
    # Override primary key dengan nama custom
    cart_item_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke Cart
    cart_id = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='cart_id',
        help_text="Cart yang memuat item ini"
    )
    
    # Foreign Key ke Product
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        db_column='product_id',
        help_text="Produk dalam cart"
    )
    
    # Kuantitas item
    qty = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Jumlah produk dalam cart"
    )
    
    # Harga saat item ditambahkan ke cart
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Harga produk pada saat ditambahkan ke cart"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal item ditambahkan ke cart"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal item di-update"
    )
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        db_table = 'cart_items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart_id']),
            models.Index(fields=['product_id']),
        ]
        unique_together = ['cart_id', 'product_id']  # Tidak boleh produk sama 2x dalam 1 cart
    
    def __str__(self):
        return f"{self.product_id.product_name} (qty: {self.qty})"


# ============================================================================
# ORDER MODEL
# ============================================================================

class Order(models.Model):
    """
    Model untuk pesanan (order) di platform B2B2C VOLTA.
    Setiap order terikat ke satu user dan satu brand.
    """
    
    # Pilihan status order
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )
    
    # Pilihan payment method
    PAYMENT_METHOD_CHOICES = (
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('e_wallet', 'E-Wallet'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    # Pilihan payment status
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    # Override primary key dengan nama custom
    order_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke User (customer)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        db_column='user_id',
        help_text="Customer yang melakukan pesanan"
    )
    
    # Foreign Key ke Brand (karena 1 order = 1 brand)
    brand_id = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='orders',
        db_column='brand_id',
        help_text="Brand/vendor penjual dalam order ini"
    )
    
    # Kode order (unik)
    order_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Kode unik order"
    )
    
    # Tanggal order
    order_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal dan waktu order dibuat"
    )
    
    # Status order
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        help_text="Status order"
    )
    
    # Total amount
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total jumlah uang order"
    )
    
    # Payment method
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        help_text="Metode pembayaran"
    )
    
    # Payment status
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Status pembayaran"
    )
    
    # Alamat pengiriman
    shipping_address = models.TextField(
        help_text="Alamat lengkap pengiriman"
    )
    
    # Nama penerima
    receiver_name = models.CharField(
        max_length=255,
        help_text="Nama penerima barang"
    )
    
    # Nomor telepon penerima
    phone = models.CharField(
        max_length=20,
        help_text="Nomor telepon penerima"
    )

    # Nomor resi pengiriman (tracking number)
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nomor resi dari kurir pengiriman"
    )

    # Alasan pembatalan
    cancel_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Alasan pembatalan order (jika applicable)"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal order dibuat"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal order terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_code']),
            models.Index(fields=['user_id']),
            models.Index(fields=['brand_id']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_code}"


# ============================================================================
# ORDER ITEM MODEL
# ============================================================================

class OrderItem(models.Model):
    """
    Model untuk item-item dalam satu pesanan (order).
    Setiap order item terikat ke order dan produk tertentu.
    """
    
    # Override primary key dengan nama custom
    order_item_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke Order
    order_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='order_id',
        help_text="Order yang memuat item ini"
    )
    
    # Foreign Key ke Product
    product_id = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        db_column='product_id',
        help_text="Produk dalam order"
    )
    
    # Harga produk pada saat order dibuat
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Harga produk pada saat order"
    )
    
    # Kuantitas produk yang dipesan
    qty = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Jumlah produk yang dipesan"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal order item dibuat"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal order item terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        db_table = 'order_items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"{self.product_id.product_name} x{self.qty}"


# ============================================================================
# REVIEW MODEL
# ============================================================================

class Review(models.Model):
    """
    Model untuk review/rating produk di platform B2B2C VOLTA.
    Setiap user dapat memberikan review untuk setiap produk.
    """
    
    # Pilihan rating
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    # Override primary key dengan nama custom
    review_id = models.AutoField(primary_key=True)
    
    # Foreign Key ke Product
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='product_id',
        help_text="Produk yang di-review"
    )
    
    # Foreign Key ke User (reviewer)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='user_id',
        help_text="User yang memberikan review"
    )
    
    # Rating (1-5)
    rating = models.SmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating produk (1-5)"
    )
    
    # Komentar review
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Komentar atau review produk"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal review dibuat"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal review terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['rating']),
        ]
        unique_together = ['product_id', 'user_id']  # Satu user hanya bisa review 1x per produk
    
    def __str__(self):
        return f"Review by {self.user_id.username} - {self.product_id.product_name} ({self.rating}⭐)"


# ============================================================================
# VENDOR REQUEST MODEL
# ============================================================================

class VendorRequest(models.Model):
    """
    Model untuk pengajuan vendor/brand dari calon seller di platform B2B2C VOLTA.
    Digunakan sebelum vendor disetujui dan mendapatkan akses brand profile.
    """
    
    # Pilihan status vendor request
    STATUS_CHOICES = (
        ('Pending', 'Menunggu Verifikasi'),
        ('Approved', 'Disetujui'),
        ('Rejected', 'Ditolak'),
    )
    
    # Foreign Key ke User (pengaju vendor request)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vendor_requests',
        db_column='user_id',
        help_text="User yang melakukan pengajuan (jika terdaftar)"
    )
    
    # Nama vendor/brand
    vendor_name = models.CharField(
        max_length=255,
        help_text="Nama Brand / Toko Resmi Elektronik"
    )
    
    # Email kontak pengaju
    email = models.EmailField(
        max_length=255,
        help_text="Alamat email pengaju yang akan digunakan untuk notifikasi dan verifikasi"
    )
    
    # NIB atau Nomor KTP
    nib = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nomor Induk Berusaha (NIB) atau Nomor KTP"
    )
    
    # Kategori utama
    category = models.CharField(
        max_length=100,
        help_text="Kategori utama elektronik yang dijual"
    )
    
    # Alamat
    address = models.TextField(
        help_text="Alamat lengkap gudang distribusi (kota, provinsi, kode pos)"
    )
    
    # Deskripsi
    description = models.TextField(
        help_text="Deskripsi latar belakang bisnis dan alasan bergabung"
    )
    
    # Status pengajuan
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Status pengajuan vendor"
    )

    # Token aktivasi untuk pengaturan akun vendor setelah disetujui
    activation_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        help_text="Token unik untuk setup akun vendor setelah pengajuan disetujui"
    )

    # Timestamp ketika token aktivasi dibuat
    token_created_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Waktu token aktivasi dibuat"
    )
    
    # Catatan admin
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Catatan dari admin untuk pengajuan ini"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal pengajuan dibuat"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal pengajuan terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('Vendor Request')
        verbose_name_plural = _('Vendor Requests')
        db_table = 'vendor_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.vendor_name} ({self.get_status_display()})"


# ============================================================================
# USER TWO-FACTOR AUTHENTICATION MODEL
# ============================================================================

class UserTwoFactor(models.Model):
    """
    Model untuk menyimpan konfigurasi Two-Factor Authentication (2FA) user.
    Setiap user hanya bisa memiliki satu konfigurasi 2FA.
    """
    
    # OneToOne ke User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='two_factor',
        db_column='user_id',
        help_text="User yang menggunakan 2FA"
    )
    
    # Status 2FA (aktif/nonaktif)
    is_enabled = models.BooleanField(
        default=False,
        help_text="Status aktivasi Two-Factor Authentication"
    )
    
    # Secret key untuk 2FA (TOTP)
    secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Secret key untuk Time-based One-Time Password (TOTP)"
    )
    
    # Backup codes (JSON atau text)
    backup_codes = models.TextField(
        blank=True,
        null=True,
        help_text="Kode backup untuk akses emergency (simpan sebagai JSON)"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal 2FA pertama kali diaktifkan"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Tanggal 2FA terakhir diperbarui"
    )
    
    class Meta:
        verbose_name = _('User Two-Factor Authentication')
        verbose_name_plural = _('User Two-Factor Authentications')
        db_table = 'user_two_factor'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_enabled']),
        ]
    
    def __str__(self):
        status = 'Enabled' if self.is_enabled else 'Disabled'
        return f"2FA {status} - {self.user.username}"


# ============================================================================
# LOGIN SESSION MODEL
# ============================================================================

class LoginSession(models.Model):
    """
    Model untuk menyimpan riwayat login session user di berbagai perangkat.
    Digunakan untuk fitur "Login Session Management" di halaman profil.
    """
    
    # Foreign Key ke User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_sessions',
        db_column='user_id',
        help_text="User yang memiliki session ini"
    )
    
    # Nama perangkat
    device_name = models.CharField(
        max_length=255,
        help_text="Nama perangkat (contoh: 'Chrome on Windows', 'Safari on iPhone')"
    )
    
    # Alamat IP
    ip_address = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Alamat IP perangkat saat login"
    )
    
    # User agent
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser user agent string"
    )
    
    # Status session (aktif/nonaktif)
    is_active = models.BooleanField(
        default=True,
        help_text="Status session saat ini (aktif atau sudah logout)"
    )
    
    # Aktivitas terakhir
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Waktu aktivitas terakhir di session ini"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Tanggal dan waktu session dibuat (saat login)"
    )
    
    class Meta:
        verbose_name = _('Login Session')
        verbose_name_plural = _('Login Sessions')
        db_table = 'login_sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.device_name} - {self.user.username} ({status})"


# ============================================================================
# EMAIL OTP MODEL
# ============================================================================

class EmailOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_otps',
        help_text="User yang menerima OTP ini"
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_otps'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"
