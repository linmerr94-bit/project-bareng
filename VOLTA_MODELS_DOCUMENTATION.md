# Platform B2B2C VOLTA - Database Models Documentation

## 📋 Ringkasan

Dokumentasi ini menjelaskan struktur model database Django untuk platform B2B2C **VOLTA**. Semua model telah dirancang sesuai dengan ERD yang disediakan dengan ketentuan:

- ✅ Primary Key custom sesuai nama (user_id, brand_id, category_id, etc.)
- ✅ Semua relasi menggunakan Foreign Key dengan nama tabel dan field yang tepat
- ✅ Timestamps untuk audit trail (created_at, updated_at)
- ✅ Status dan validation fields sesuai kebutuhan bisnis

---

## 🔐 1. User Model (`users/models.py`)

Model User custom yang extends `AbstractUser` dengan role-based access control.

### Struktur Tabel: `users`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `user_id` | AutoField (PK) | Primary Key | ID unik pengguna |
| `username` | CharField(150) | Unique | Username untuk login |
| `email` | EmailField | Unique | Email pengguna |
| `password` | CharField | Hashed | Password terenkripsi |
| `role` | CharField(20) | Choices: admin, brand, customer | Role dalam sistem |
| `full_name` | CharField(255) | Nullable | Nama lengkap |
| `phone` | CharField(20) | Unique, Nullable | Nomor telepon |
| `is_active` | BooleanField | Default: True | Status aktif |
| `is_staff` | BooleanField | Default: False | Akses admin Django |
| `is_superuser` | BooleanField | Default: False | Superuser status |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Relasi
- OneToOne → `Brands.user_id` (optional)
- OneToOne → `Carts.user_id` (optional)
- ForeignKey ← `Orders.user_id`
- ForeignKey ← `Reviews.user_id`
- ForeignKey ← `Brands.approved_by` (optional, admin yang approve)

---

## 🏢 2. Brands Model (`master_products/models.py`)

Model untuk profil brand/vendor yang menjual produk.

### Struktur Tabel: `brands`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `brand_id` | AutoField (PK) | Primary Key | ID unik brand |
| `user_id` | OneToOneField | FK → users(user_id), Unique | Pemilik brand |
| `brand_name` | CharField(255) | Required | Nama brand |
| `logo` | ImageField | Nullable | Logo brand |
| `description` | TextField | Nullable | Deskripsi brand |
| `status` | CharField(20) | Choices: pending, approved, rejected | Status approval |
| `approved_at` | DateTimeField | Nullable | Waktu persetujuan |
| `approved_by` | ForeignKey | FK → users(user_id), Nullable | Admin yang approve |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Relasi
- OneToOne → `Users.brand_profile`
- ForeignKey ← `Products.brand_id`
- ForeignKey ← `Orders.brand_id`

---

## 📂 3. Categories Model (`master_products/models.py`)

Model untuk kategori produk.

### Struktur Tabel: `categories`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `category_id` | AutoField (PK) | Primary Key | ID unik kategori |
| `category_name` | CharField(255) | Unique | Nama kategori |
| `description` | TextField | Nullable | Deskripsi kategori |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Relasi
- ForeignKey ← `Products.category_id`

---

## 📦 4. Products Model (`master_products/models.py`)

Model untuk produk yang dijual oleh brand.

### Struktur Tabel: `products`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `product_id` | AutoField (PK) | Primary Key | ID unik produk |
| `brand_id` | ForeignKey | FK → brands(brand_id), CASCADE | Brand penjual |
| `category_id` | ForeignKey | FK → categories(category_id), PROTECT | Kategori produk |
| `product_name` | CharField(255) | Required | Nama produk |
| `slug` | SlugField(255) | Unique | URL-friendly ID |
| `description` | TextField | Required | Deskripsi detail |
| `price` | DecimalField(12,2) | Min: 0 | Harga jual |
| `stock` | IntegerField | Min: 0, Default: 0 | Stok tersedia |
| `image` | ImageField | Nullable | Foto produk |
| `is_active` | BooleanField | Default: True | Status aktif |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Relasi
- ForeignKey → `Brands.products`
- ForeignKey → `Categories.products`
- ForeignKey ← `CartItems.product_id`
- ForeignKey ← `OrderItems.product_id`
- ForeignKey ← `Reviews.product_id`

---

## 🛒 5. Carts Model (`master_products/models.py`)

Model untuk shopping cart pengguna.

### Struktur Tabel: `carts`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `cart_id` | AutoField (PK) | Primary Key | ID unik cart |
| `user_id` | OneToOneField | FK → users(user_id), Unique, CASCADE | Pemilik cart |

### Relasi
- OneToOne → `Users.cart`
- ForeignKey ← `CartItems.cart_id`

---

## 🏷️ 6. CartItems Model (`master_products/models.py`)

Model untuk item individual dalam shopping cart.

### Struktur Tabel: `cart_items`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `cart_item_id` | AutoField (PK) | Primary Key | ID unik cart item |
| `cart_id` | ForeignKey | FK → carts(cart_id), CASCADE | Cart yang memiliki |
| `product_id` | ForeignKey | FK → products(product_id), CASCADE | Produk dalam cart |
| `qty` | IntegerField | Min: 1, Default: 1 | Jumlah item |
| `price` | DecimalField(12,2) | Min: 0 | Harga saat ditambah |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Constraints
- `UNIQUE(cart_id, product_id)` - Satu produk hanya sekali per cart

### Relasi
- ForeignKey → `Carts.items`
- ForeignKey → `Products.cart_items`

---

## 📋 7. Orders Model (`master_products/models.py`)

Model untuk pesanan/order.

### Struktur Tabel: `orders`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `order_id` | AutoField (PK) | Primary Key | ID unik order |
| `user_id` | ForeignKey | FK → users(user_id), PROTECT | Pembeli |
| `brand_id` | ForeignKey | FK → brands(brand_id), PROTECT | Brand penjual |
| `order_code` | CharField(50) | Unique | Kode order unik |
| `order_date` | DateTimeField | Auto | Waktu order dibuat |
| `status` | CharField(20) | Choices (7 nilai) | Status order |
| `total_amount` | DecimalField(12,2) | Min: 0 | Total harga |
| `payment_method` | CharField(50) | Choices (5 metode) | Metode pembayaran |
| `payment_status` | CharField(20) | Choices: pending, paid, failed, refunded | Status pembayaran |
| `shipping_address` | TextField | Required | Alamat pengiriman |
| `receiver_name` | CharField(255) | Required | Nama penerima |
| `phone` | CharField(20) | Required | Telepon penerima |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Status Order Options
- `pending` - Menunggu konfirmasi
- `confirmed` - Dikonfirmasi
- `processing` - Sedang diproses
- `shipped` - Sudah dikirim
- `delivered` - Diterima
- `cancelled` - Dibatalkan
- `returned` - Dikembalikan

### Payment Method Options
- `bank_transfer` - Transfer Bank
- `credit_card` - Kartu Kredit
- `debit_card` - Kartu Debit
- `e_wallet` - E-Wallet
- `cash_on_delivery` - Bayar di Tempat

### Relasi
- ForeignKey → `Users.orders`
- ForeignKey → `Brands.orders`
- ForeignKey ← `OrderItems.order_id`

---

## 📦 8. OrderItems Model (`master_products/models.py`)

Model untuk item individual dalam order.

### Struktur Tabel: `order_items`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `order_item_id` | AutoField (PK) | Primary Key | ID unik order item |
| `order_id` | ForeignKey | FK → orders(order_id), CASCADE | Order yang memiliki |
| `product_id` | ForeignKey | FK → products(product_id), PROTECT | Produk dipesan |
| `price` | DecimalField(12,2) | Min: 0 | Harga saat order |
| `qty` | IntegerField | Min: 1, Default: 1 | Jumlah dipesan |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Relasi
- ForeignKey → `Orders.items`
- ForeignKey → `Products.order_items`

---

## ⭐ 9. Reviews Model (`master_products/models.py`)

Model untuk review/rating produk.

### Struktur Tabel: `reviews`

| Field | Type | Constraints | Deskripsi |
|-------|------|-------------|-----------|
| `review_id` | AutoField (PK) | Primary Key | ID unik review |
| `product_id` | ForeignKey | FK → products(product_id), CASCADE | Produk direview |
| `user_id` | ForeignKey | FK → users(user_id), CASCADE | Pemberi review |
| `rating` | SmallIntegerField | Choices: 1-5, Required | Rating 1-5 bintang |
| `comment` | TextField | Nullable | Komentar review |
| `created_at` | DateTimeField | Auto | Waktu pembuatan |
| `updated_at` | DateTimeField | Auto | Waktu update terakhir |

### Rating Choices
- `1` - Poor (Buruk)
- `2` - Fair (Cukup)
- `3` - Good (Baik)
- `4` - Very Good (Sangat Baik)
- `5` - Excellent (Luar Biasa)

### Constraints
- `UNIQUE(product_id, user_id)` - Satu user hanya review 1x per produk

### Relasi
- ForeignKey → `Products.reviews`
- ForeignKey → `Users.reviews`

---

## 🔍 Database Indexes

Untuk optimasi query, semua model memiliki indexes pada field yang sering di-query:

### User Indexes
- `email`
- `role`
- `is_active`

### Brands Indexes
- `status`
- `user_id`
- `created_at`

### Products Indexes
- `slug`
- `brand_id`
- `category_id`
- `is_active`

### Orders Indexes
- `order_code`
- `user_id`
- `brand_id`
- `status`
- `payment_status`

### Reviews Indexes
- `product_id`
- `user_id`
- `rating`

---

## 🚀 Cara Menggunakan

### 1. Setup Database

```bash
# Buat migration
python manage.py makemigrations users master_products

# Apply migration
python manage.py migrate
```

### 2. Create Admin User

```bash
python manage.py createsuperuser
```

### 3. Access Admin Panel

- URL: `http://localhost:8000/admin/`
- Kelola semua models melalui Django Admin Interface

---

## 📊 Relasi Model (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS (user_id PK)                   │
├──────────────────────────────────────────────────────────────┤
│ Roles: admin, brand, customer                                │
│ Has: phone, full_name, role, is_active, timestamps           │
└──────────────┬────────────────────────────────┬──────────────┘
               │ 1:1                     1:N   │
               │                              │
       ┌───────▼────────────┐      ┌──────────▼────────────┐
       │  BRANDS(brand_id)  │      │  CARTS(cart_id)      │
       ├────────────────────┤      ├──────────────────────┤
       │ 1:N                │      │ 1:N                  │
       │ user_id (FK)       │      │ user_id (FK, U)      │
       │ status             │      │                      │
       │ approved_by (FK)   │      │  CartItems           │
       └───────┬────────────┘      │  ├─ qty              │
               │                   │  ├─ price           │
               │ 1:N               │  └─ product_id (FK)  │
       ┌───────▼──────────────┐    └──────────────────────┘
       │PRODUCTS(product_id)  │
       ├──────────────────────┤      ┌──────────────────────┐
       │ brand_id (FK)        │      │ORDERS(order_id)      │
       │ category_id (FK)     │      ├──────────────────────┤
       │ slug (U)             │      │ user_id (FK)         │
       │ price, stock         │      │ brand_id (FK)        │
       │ is_active            │      │ status, payment_*    │
       │                      │      │ shipping_address     │
       │  CartItems (1:N)     │      │ receiver_name, phone │
       │  OrderItems (1:N)    │      │ total_amount         │
       │  Reviews (1:N)       │      │                      │
       └───────┬──────────────┘      │  OrderItems          │
               │                    │  ├─ qty              │
               │ 1:N                │  ├─ price            │
       ┌───────▼──────────────┐     │  └─ product_id (FK)  │
       │CATEGORIES(category_id)│    └──────────────────────┘
       ├──────────────────────┤
       │ category_name (U)    │
       │ description          │
       └──────────────────────┘

┌────────────────────────┐
│ REVIEWS(review_id)     │
├────────────────────────┤
│ product_id (FK)        │
│ user_id (FK)           │
│ rating (1-5)           │
│ comment                │
│ U: product_id+user_id  │
└────────────────────────┘
```

---

## ⚙️ Konfigurasi Django

Pada `core_system/settings.py`:

```python
# Custom User Model
AUTH_USER_MODEL = 'users.User'

# INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'users.apps.UsersConfig',
    'master_products.apps.MasterProductsConfig',
]
```

---

## 📝 Notes Penting

1. **Primary Keys**: Semua model menggunakan custom primary key sesuai nama (user_id, brand_id, dll)
2. **Foreign Keys**: Semua FK menggunakan `db_column` untuk nama yang konsisten
3. **Timestamps**: Semua model memiliki `created_at` (auto_now_add) dan `updated_at` (auto_now)
4. **Unique Constraints**: Diterapkan pada field yang seharusnya unik (email, phone, slug, order_code)
5. **Indexes**: Pada field yang sering di-filter/search untuk optimasi performa
6. **Cascade Delete**: Diterapkan dengan hati-hati untuk menjaga integritas data
7. **Validators**: Min/Max validators untuk numeric fields

---

## 🎯 Next Steps

1. ✅ Models sudah dibuat
2. ⏳ Run migrations: `python manage.py migrate`
3. ⏳ Create superuser untuk testing admin
4. ⏳ Create API endpoints (jika menggunakan DRF)
5. ⏳ Create views dan templates untuk frontend
6. ⏳ Implement authentication & authorization
7. ⏳ Create business logic & services

---

**Terakhir Update**: June 5, 2026  
**Platform**: B2B2C VOLTA  
**Django Version**: 6.0.5  
**Python**: 3.11+
