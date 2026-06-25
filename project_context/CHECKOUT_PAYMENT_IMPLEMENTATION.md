# CHECKOUT & PAYMENT SIMULATOR - QUICK START GUIDE

## ✅ Implementation Complete

Semua file sudah dibuat dan siap digunakan. Berikut adalah ringkasan lengkap:

---

## 📦 Files Created/Modified

### Views (`master_products/views.py`)
- ✅ Added imports: `Order`, `OrderItem`, `Brand`, `transaction`, `timezone`, `uuid`
- ✅ Added 5 new functions:
  1. `checkout_view()` - Form checkout & create order
  2. `process_payment_view()` - Payment simulator
  3. `order_confirmation_view()` - Success page
  4. `order_list_view()` - Order history
  5. `order_detail_view()` - Order details

### URLs (`master_products/urls.py`)
- ✅ Added 5 new routes:
  - `/checkout/` → checkout_view
  - `/payment/<int:order_id>/` → process_payment_view
  - `/order-confirmation/<int:order_id>/` → order_confirmation_view
  - `/orders/` → order_list_view
  - `/order/<int:order_id>/` → order_detail_view

### Templates (5 NEW files)
- ✅ `checkout.html` - Checkout form
- ✅ `payment.html` - Payment simulator
- ✅ `order_confirmation.html` - Success page
- ✅ `order_list.html` - Order history
- ✅ `order_detail.html` - Order details

### Other
- ✅ `cart.html` - UPDATED (checkout button link)

---

## 🚀 How to Test

### Step 1: Database Reset (Optional - untuk clean state)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Test Data
```powershell
python manage.py shell
```

```python
from users.models import User
from master_products.models import Category, Brand, Product

# 1. Create test user
user = User.objects.create_user(
    username='test@test.com',
    email='test@test.com',
    password='test1234',
    role='customer'
)

# 2. Create test brand & products
from django.contrib.auth import get_user_model
User2 = get_user_model()
vendor = User2.objects.create_user(
    username='vendor@test.com',
    email='vendor@test.com',
    password='test1234',
    role='brand'
)

# 3. Create category
cat = Category.objects.create(category_name='Smartphone')

# 4. Create brand (from master_products)
brand = Brand.objects.create(
    user_id=vendor,
    brand_name='Test Brand',
    status='approved'
)

# 5. Create product
product = Product.objects.create(
    brand_id=brand,
    category_id=cat,
    product_name='Test Phone',
    slug='test-phone',
    description='Test Description',
    price=5000000,
    stock=10,
    is_active=True
)

exit()
```

### Step 3: Run Server
```powershell
python manage.py runserver
```

### Step 4: Test Flow

1. **Navigate to**: `http://127.0.0.1:8000/`
2. **Click**: Katalog Produk → Login (use test@test.com / test1234)
3. **Browse**: Lihat produk list
4. **Add**: Klik produk → Tambah ke Keranjang
5. **View Cart**: Klik Keranjang (top-right)
6. **Checkout**: Klik "Lanjut ke Pembayaran"
7. **Fill Form**: 
   - Nama Penerima: Budi Santoso
   - Nomor Telepon: 081234567890
   - Alamat Lengkap: Jl. Test No. 123, Jakarta
   - Metode Pembayaran: Bank Transfer
8. **Submit**: Klik "Lanjut ke Pembayaran"
9. **Payment Simulator**: Klik "Simulasikan Pembayaran"
10. **Confirmation**: Lihat halaman sukses
11. **History**: Klik "Riwayat Pesanan" → Lihat order list
12. **Detail**: Klik "Lihat Detail" → Lihat order details

---

## 🔍 Verification Checklist

### After Checkout (Step 8)
```
✅ Order created with status='pending'
✅ Product stock decremented
✅ CartItem cleared
✅ OrderItem created
✅ Redirect to payment page successful
```

### After Payment (Step 9)
```
✅ Order status updated to 'confirmed'
✅ Payment status updated to 'paid'
✅ Redirect to confirmation page
✅ Order code displayed
✅ Total amount shown
```

### Order List (Step 11)
```
✅ Order appears in list
✅ Status badge correct
✅ Total amount correct
✅ Link to detail works
```

### Order Detail (Step 12)
```
✅ All order items displayed
✅ Shipping address correct
✅ Brand info shown
✅ Payment info displayed
✅ Timeline status visible
```

---

## 🐛 Troubleshooting

### Error: "Cart not found"
- Ensure user is logged in
- Check if user has cart created

### Error: "Stock not sufficient"
- Go back to cart
- Reduce quantity
- Try checkout again

### Error: "Access denied"
- Try to access someone else's order
- You can only view your own orders
- Login with correct account

### Templates not found
- Ensure all 5 templates created in: `master_products/templates/master_products/`
- Check file names match exactly

### URLs not working
- Ensure urls.py updated with all 5 routes
- Check app_name = 'master_products'
- Test: `django.urls.reverse('master_products:checkout')`

---

## 💾 Database Schema (Auto-generated)

### Order Table
```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    brand_id INTEGER,
    order_code VARCHAR(50) UNIQUE,
    total_amount DECIMAL,
    status VARCHAR(20),
    payment_status VARCHAR(20),
    payment_method VARCHAR(50),
    shipping_address TEXT,
    receiver_name VARCHAR(255),
    phone VARCHAR(20),
    order_date DATETIME,
    created_at DATETIME,
    updated_at DATETIME
)
```

### OrderItem Table
```sql
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    price DECIMAL,
    qty INTEGER,
    created_at DATETIME,
    updated_at DATETIME
)
```

---

## 📱 Response Examples

### POST /checkout/ - Success
```json
{
    "status": "success",
    "order_id": 1,
    "order_code": "ORD-1719000000-ABC123",
    "total": 5000000,
    "redirect": "/payment/1/"
}
```

### POST /payment/<id>/ - Success
```json
{
    "status": "success",
    "message": "Pembayaran berhasil",
    "order_status": "confirmed",
    "payment_status": "paid",
    "redirect": "/order-confirmation/1/"
}
```

---

## 🎯 Next Phase Implementation

### Phase 2 (Post-demo):
1. Payment gateway integration (Midtrans)
2. Email notifications
3. Vendor order management
4. Review & rating system
5. Return/refund flow
6. Cart item AJAX update
7. Inventory alerts

---

## 📞 Support

**Issues?** Check Django debug toolbar:
```python
# Add to settings.py for development
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

Then access: `http://127.0.0.1:8000/__debug__/`

---

## ✨ Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Checkout form | ✅ Complete | Form validation included |
| Stock validation | ✅ Complete | Double-check in transaction |
| Order creation | ✅ Complete | Atomic transaction used |
| Payment simulator | ✅ Complete | Dummy payment processor |
| Order confirmation | ✅ Complete | Success page with details |
| Order history | ✅ Complete | List all customer orders |
| Order tracking | ✅ Complete | Detailed order view |
| Permission check | ✅ Complete | User can only see own orders |
| Email notifications | ❌ TODO | Phase 2 |
| Payment gateway | ❌ TODO | Phase 2 (Midtrans) |
| Vendor order mgmt | ❌ TODO | Phase 2 |

---

## 🎉 Ready to Demo!

Semua file sudah siap. Aplikasi ini sudah bisa:
- ✅ Customer checkout
- ✅ Simulasi pembayaran
- ✅ Track order
- ✅ View order history

**Target completion**: 30 Juni 2026 ✓
**MVP Status**: READY FOR DEMO

