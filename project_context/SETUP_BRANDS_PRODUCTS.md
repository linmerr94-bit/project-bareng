# Setup Django Apps: Brands & Products

Dokumentasi lengkap untuk setup aplikasi `brands` dan `products`.

## Struktur File yang Telah Dibuat

### Aplikasi `brands/`
```
brands/
├── __init__.py
├── admin.py          (Admin interface untuk BrandProfile)
├── apps.py           (Konfigurasi app)
├── models.py         (Model BrandProfile)
├── tests.py          (Unit tests)
├── views.py          (Views & API endpoints)
└── migrations/       (Akan dibuat otomatis oleh Django)
```

### Aplikasi `products/`
```
products/
├── __init__.py
├── admin.py          (Admin interface untuk Category & Product)
├── apps.py           (Konfigurasi app)
├── models.py         (Model Category & Product)
├── tests.py          (Unit tests)
├── views.py          (Views & API endpoints)
└── migrations/       (Akan dibuat otomatis oleh Django)
```

---

## Langkah-Langkah Setup

### 1. Update `settings.py`
Tambahkan kedua app ke dalam `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... apps lainnya
    'brands.apps.BrandsConfig',
    'products.apps.ProductsConfig',
]
```

### 2. Buat Database Migrations
Jalankan perintah berikut di terminal:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. (Opsional) Update `admin.py` Project
Jika ingin meakses admin dengan URL default, pastikan file `core_system/urls.py` sudah include admin:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... urls lainnya
]
```

---

## Model Details

### BrandProfile (brands/models.py)

**Field:**
- `user`: OneToOneField ke AUTH_USER_MODEL (Pemilik brand)
- `brand_name`: CharField (Nama unik brand)
- `nib_or_ktp`: CharField (Nomor identitas untuk verifikasi - NIB atau KTP)
- `rating`: FloatField (Default 0.0, untuk rating dari customer)
- `status`: CharField dengan choices:
  - `PENDING`: Menunggu persetujuan admin
  - `APPROVED`: Sudah disetujui admin
  - `SUSPENDED`: Brand ditangguhkan
- `created_at`: DateTimeField (Auto)
- `updated_at`: DateTimeField (Auto)

**Relasi:**
- Terhubung ke `User` (1:1) untuk seller/brand owner

---

### Category (products/models.py)

**Field:**
- `name`: CharField (Nama kategori - unique)
- `description`: TextField (Opsional)
- `is_active`: BooleanField (Default True)
- `created_at`: DateTimeField (Auto)
- `updated_at`: DateTimeField (Auto)

**Contoh kategori:**
- Smartphone
- Laptop
- TV
- AC
- Kulkas
- Washing Machine
- dll

---

### Product (products/models.py)

**Field:**
- `brand`: ForeignKey ke BrandProfile
- `category`: ForeignKey ke Category
- `name`: CharField (Nama produk)
- `sku`: CharField (Stock Keeping Unit - unique)
- `description`: TextField
- **`price_b2c`** (REQ-F009): DecimalField - Harga eceran (konsumen individual)
- **`price_b2b`** (REQ-F009): DecimalField - Harga grosir (pembeli bulk)
- **`moq_b2b`** (REQ-F010): PositiveIntegerField - Minimum Order Quantity untuk harga B2B
- **`stock`** (REQ-F010): PositiveIntegerField - Jumlah stok tersedia
- `is_active`: BooleanField (Default True)
- `rating`: FloatField (Default 0.0, range 0.0-5.0)
- `created_at`: DateTimeField (Auto)
- `updated_at`: DateTimeField (Auto)

**Constraints:**
- `price_b2b` harus <= `price_b2c` (harga grosir tidak boleh lebih mahal)
- `moq_b2b` minimal 1

**Method:**
- `get_price_for_quantity(quantity)`: Menentukan harga berdasarkan jumlah pemesanan
  - Jika quantity >= moq_b2b → gunakan price_b2b
  - Jika quantity < moq_b2b → gunakan price_b2c

---

## Penggunaan di Views/Serializers

### Contoh Query di Views

```python
from brands.models import BrandProfile
from products.models import Category, Product

# Get semua brand yang approved
approved_brands = BrandProfile.objects.filter(status='APPROVED')

# Get produk dari brand tertentu
products = Product.objects.filter(brand=brand_id, is_active=True)

# Get produk dengan kategori tertentu
electronics = Product.objects.filter(category__name='Smartphone')

# Get harga berdasarkan quantity
product = Product.objects.get(sku='SKU123')
quantity = 10
price = product.get_price_for_quantity(quantity)
```

### Contoh untuk DRF Serializers

```python
from rest_framework import serializers
from brands.models import BrandProfile
from products.models import Product

class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = ['id', 'brand_name', 'rating', 'status', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.brand_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'brand_name', 'category_name',
            'price_b2c', 'price_b2b', 'moq_b2b', 'stock',
            'is_active', 'rating'
        ]
```

---

## Admin Interface

### Akses Django Admin
1. Buat superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Jalankan development server:
   ```bash
   python manage.py runserver
   ```

3. Akses http://localhost:8000/admin/

### Admin Features
- **BrandProfile Admin**: List dengan filter status, search, readonly timestamps
- **Category Admin**: List dengan filter status
- **Product Admin**: List dengan filter lengkap, grouped fieldsets sesuai SRS requirements

---

## Notes Penting

✅ **REQ-F009 Implementation:**
- Field `price_b2c` untuk harga eceran
- Field `price_b2b` untuk harga grosir
- Constraint database untuk validasi price_b2b <= price_b2c

✅ **REQ-F010 Implementation:**
- Field `moq_b2b` untuk minimum order quantity grosir
- Field `stock` untuk tracking inventori
- Method `get_price_for_quantity()` untuk dynamic pricing

✅ **REQ-F001 Implementation:**
- Model `BrandProfile` dengan status workflow (PENDING → APPROVED/SUSPENDED)
- Admin interface untuk manage brand

---

## Testing (Optional)

Contoh test case di `tests.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from brands.models import BrandProfile
from products.models import Product, Category

User = get_user_model()

class BrandProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller1', password='pass123')
        self.brand = BrandProfile.objects.create(
            user=self.user,
            brand_name='ElectroShop',
            nib_or_ktp='1234567890',
            status='APPROVED'
        )
    
    def test_brand_creation(self):
        self.assertEqual(self.brand.brand_name, 'ElectroShop')
        self.assertEqual(self.brand.rating, 0.0)

class ProductTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller1', password='pass123')
        self.brand = BrandProfile.objects.create(
            user=self.user,
            brand_name='ElectroShop',
            nib_or_ktp='1234567890'
        )
        self.category = Category.objects.create(name='Smartphone')
        self.product = Product.objects.create(
            brand=self.brand,
            category=self.category,
            name='iPhone 15',
            sku='IPHONE15',
            description='Latest iPhone',
            price_b2c=15000000,
            price_b2b=14000000,
            moq_b2b=5,
            stock=100
        )
    
    def test_price_calculation(self):
        # Quantity kurang dari MOQ → gunakan B2C price
        price = self.product.get_price_for_quantity(3)
        self.assertEqual(price, 15000000)
        
        # Quantity >= MOQ → gunakan B2B price
        price = self.product.get_price_for_quantity(5)
        self.assertEqual(price, 14000000)
```

---

## Troubleshooting

**Error: "ModuleNotFoundError: No module named 'brands'"**
- Pastikan sudah menambahkan apps ke INSTALLED_APPS di settings.py

**Error: "IntegrityError pada migration"**
- Pastikan tidak ada data existing yang conflict
- Hapus db.sqlite3 dan jalankan migrate dari awal

**Harga B2B lebih besar dari B2C**
- Constraint database akan mencegah ini
- Validasi akan error jika mencoba save data invalid

---

**Setup selesai! Anda sekarang siap untuk:**
1. Membuat custom views/API endpoints
2. Membuat DRF Serializers
3. Membuat URL routing
4. Membuat unit tests
5. Deploy ke production

Untuk pertanyaan lebih lanjut, silakan refer ke file models.py untuk dokumentasi inline lengkap.
