# ✅ VOLTA Audit Verification Checklist

Use this checklist to verify all audit findings are accurate.

---

## 🧪 Part 1: User Model & Test Accounts

### 1.1 User Model Structure
```bash
# Check custom User model
cd d:\PROJEK UAS E-COMMERCE
python manage.py shell

>>> from users.models import User
>>> User._meta.fields
# Should show: user_id, role, full_name, phone, and all standard fields

>>> # Check role choices
>>> User.ROLE_CHOICES
# Should show: ('admin', ...), ('brand', ...), ('customer', ...)

>>> # Verify test users exist
>>> User.objects.filter(username__in=['admin_volta', 'seller_volta']).values('username', 'role', 'email', 'is_staff')
```

**Expected Results**:
- [ ] `role` field exists and has 3 choices
- [ ] `admin_volta` exists with role='admin', is_staff=True
- [ ] `seller_volta` exists with role='brand', is_staff=False

### 1.2 Seed Data Verification
```bash
>>> from users.models import User
>>> from master_products.models import Brand

>>> # Check seed accounts
>>> User.objects.filter(username__startswith='samsung').values('username', 'role', 'email')
>>> User.objects.filter(username__startswith='apple').values('username', 'role', 'email')
>>> User.objects.filter(username__startswith='asus').values('username', 'role', 'email')

>>> # Check brands
>>> Brand.objects.all().values('brand_name', 'user_id__username', 'status')
```

**Expected Results**:
- [ ] 3 seed vendor accounts exist (samsung_store, apple_authorized, asus_official)
- [ ] All have role='brand'
- [ ] All linked brands have status='approved'

### 1.3 Test Users Count
```bash
>>> from users.models import User
>>> total = User.objects.count()
>>> admins = User.objects.filter(role='admin').count()
>>> brands = User.objects.filter(role='brand').count()
>>> customers = User.objects.filter(role='customer').count()

>>> print(f"Total: {total}, Admins: {admins}, Brands: {brands}, Customers: {customers}")
```

**Expected Results**:
- [ ] Total users ≥ 5
- [ ] Admins = 1-2
- [ ] Brands = 3-4
- [ ] Customers = 0+

---

## 🏗️ Part 2: Multi-Vendor Architecture

### 2.1 Brand Model
```bash
>>> from master_products.models import Brand
>>> Brand._meta.fields
# Should include: brand_id, user_id (OneToOne), brand_name, status, approved_by, nib_or_ktp

>>> # Check relationship
>>> Brand.objects.first().user_id
# Should return User object

>>> # Check unique constraint
>>> brand = Brand.objects.first()
>>> print(brand.user_id, "can only have ONE brand")
```

**Expected Results**:
- [ ] `user_id` is OneToOneField
- [ ] `status` has 4 choices (pending, approved, rejected, suspended)
- [ ] `nib_or_ktp` is unique
- [ ] Each user can only have ONE brand

### 2.2 Order Model Single-Vendor
```bash
>>> from master_products.models import Order
>>> Order._meta.fields
# Should include: order_id, user_id (ForeignKey), brand_id (ForeignKey), order_code

>>> # Check constraints
>>> Order._meta.get_field('order_code').unique
# Should be True

>>> # Verify single-brand per order design
>>> orders = Order.objects.all()
>>> for order in orders:
...     items = order.items.all()
...     brands = set(item.product_id.brand_id_id for item in items)
...     assert len(brands) == 1, f"Order {order.order_id} has {len(brands)} brands!"
```

**Expected Results**:
- [ ] Each order has exactly ONE brand_id
- [ ] order_code is unique
- [ ] All items in an order are from same brand

### 2.3 Decorators
```bash
>>> from master_products.decorators import role_required, seller_required, admin_required, customer_required
>>> import inspect

>>> # Check decorators exist
>>> print("role_required:", callable(role_required))
>>> print("seller_required:", callable(seller_required))
>>> print("admin_required:", callable(admin_required))
>>> print("customer_required:", callable(customer_required))
```

**Expected Results**:
- [ ] All 4 decorators callable
- [ ] `@seller_required` = `@role_required('brand')`
- [ ] `@admin_required` = `@role_required('admin')`
- [ ] `@customer_required` = `@role_required('customer')`

### 2.4 Protected Views
```bash
>>> from master_products.views import seller_dashboard, edit_product, delete_product

>>> # Check decorators applied (look at source)
>>> import inspect
>>> source = inspect.getsource(seller_dashboard)
>>> print("@seller_required in source:", "@seller_required" in source or "@login_required" in source)
```

**Expected Results**:
- [ ] `seller_dashboard` has decorators
- [ ] `edit_product` has decorators
- [ ] `delete_product` has decorators

---

## 💬 Part 3: Communication Features

### 3.1 Chat Widget
```bash
# Check if chat widget code exists in templates
cd d:\PROJEK UAS E-COMMERCE\master_products\templates\master_products

# Search for chat widget
findstr /M "floating-chat\|openChat\|closeChat" *.html
# Linux: grep -l "floating-chat\|openChat\|closeChat" *.html
```

**Expected Results**:
- [ ] Chat widget CSS found in product_list.html
- [ ] Chat JavaScript functions found
- [ ] Chat modal HTML exists

### 3.2 Chat Implementation
```bash
# In templates, look for:
# 1. <div class="floating-chat"> - floating button
# 2. <div id="chatModal"> - modal container
# 3. function openChat() - JS function
# 4. function closeChat() - JS function
```

**Expected Results**:
- [ ] Floating button visible
- [ ] Modal opens/closes via buttons
- [ ] Only UI simulation, no backend calls

### 3.3 Support Email References
```bash
# Find all support email references
cd d:\PROJEK UAS E-COMMERCE
findstr /R "support@volta" master_products/views.py
# Linux: grep -n "support@volta" master_products/views.py
```

**Expected Results**:
- [ ] `support@volta.com` found in views (at least 2-3 locations)
- [ ] Used in error/warning messages
- [ ] No actual email service configured

### 3.4 Chat Limitations
```bash
# Check if messaging app exists
ls -la master_products/
# Should NOT see: messages/, chat/, messaging/
```

**Expected Results**:
- [ ] No separate messaging app
- [ ] No messaging models
- [ ] No WebSocket/real-time backend

---

## 🗂️ Part 4: Code & Files

### 4.1 View Functions Count
```bash
# Count view functions
cd d:\PROJEK UAS E-COMMERCE
# PowerShell:
(Select-String "^def " master_products/views.py).Count

# Linux/Mac:
grep -c "^def " master_products/views.py
```

**Expected Result**:
- [ ] 36 functions found

### 4.2 URL Patterns Count
```bash
# PowerShell:
(Select-String "path\(" master_products/urls.py).Count

# Linux/Mac:
grep -c "path(" master_products/urls.py
```

**Expected Result**:
- [ ] ~51 paths found

### 4.3 Templates Count
```bash
# PowerShell:
(Get-ChildItem master_products/templates/master_products/*.html).Count

# Linux/Mac:
ls master_products/templates/master_products/*.html | wc -l
```

**Expected Result**:
- [ ] 29 templates found

### 4.4 Orphaned Templates
```bash
# Templates that should exist but might be unused
ls master_products/templates/master_products/ | grep -E "sprylo|simplified|detailed"
```

**Expected Results**:
- [ ] `product_detail_sprylo.html` exists
- [ ] `product_detail_simplified.html` exists
- [ ] `cart_sprylo.html` exists
- [ ] `checkout_detailed.html` exists
- [ ] None are referenced in views.py

### 4.5 Backup/Legacy Files
```bash
# Check for backup files
ls -la master_products/ | grep -i backup
ls -la *.py | grep -i backup

# Should find:
# - models_backup.py
# - db_backup_before_consolidation.sqlite3
```

**Expected Results**:
- [ ] `models_backup.py` exists
- [ ] `db_backup_before_consolidation.sqlite3` exists

### 4.6 Duplicate Models
```bash
# Check for duplicate BrandProfile
grep -n "class BrandProfile" master_products/models.py
grep -n "class BrandProfile" brands/models.py
```

**Expected Results**:
- [ ] BrandProfile found in master_products/models.py (actual)
- [ ] BrandProfile found in brands/models.py (legacy)

---

## 🔄 Part 5: Migrations

### 5.1 Migration Files
```bash
# List migrations
ls master_products/migrations/ | grep -E "\.py$"
```

**Expected Results**:
- [ ] 0001_initial.py
- [ ] 0002_add_nib_rating_to_brand.py
- [ ] 0003_migrate_brandprofile_to_brand.py (legacy)
- [ ] 0004_order_cancel_reason_order_tracking_number.py

### 5.2 Applied Migrations
```bash
python manage.py showmigrations master_products

# Should show all migrations as [X] (applied)
```

**Expected Results**:
- [ ] All migrations marked as applied [X]

---

## 🧪 Part 6: Functional Testing

### 6.1 Login Flow
```bash
# 1. Start server
python manage.py runserver

# 2. Test admin login
# URL: http://localhost:8000/master_products/login/
# Username: admin_volta
# Password: admin123
# Expected: Redirect to admin_platform_dashboard

# 3. Test seller login
# Username: seller_volta
# Password: seller123
# Expected: Redirect to seller_dashboard

# 4. Test customer login
# (Create a customer account first or register new)
# Expected: Redirect to product_list
```

**Expected Results**:
- [ ] Admin login works → admin dashboard
- [ ] Seller login works → seller dashboard
- [ ] Customer login works → product list

### 6.2 Product Catalog
```bash
# 1. Navigate to http://localhost:8000/master_products/
# 2. Should see products from seed data
# 3. Search and filter should work
# 4. Store details should be accessible
```

**Expected Results**:
- [ ] Products visible
- [ ] Search works
- [ ] Store details accessible

### 6.3 Shopping Cart
```bash
# 1. Login as customer
# 2. Add product to cart
# 3. View cart
# 4. Checkout process
```

**Expected Results**:
- [ ] Add to cart works
- [ ] Cart view shows items
- [ ] Checkout redirects to payment simulator

### 6.4 Chat Widget
```bash
# 1. Visit product_list page
# 2. Look for chat icon (bottom right)
# 3. Click to open
# 4. Send message
# 5. Verify bot response appears
```

**Expected Results**:
- [ ] Chat button visible
- [ ] Modal opens/closes
- [ ] Messages display (hardcoded responses)

---

## 📋 Summary Checklist

### Critical ✅
- [ ] 3 user roles working (admin, brand, customer)
- [ ] Test accounts exist and functional
- [ ] Multi-vendor architecture enforced (single brand per order)
- [ ] Decorators protecting seller views
- [ ] 36 views all implemented
- [ ] 51 URL patterns all mapped

### Important ⚠️
- [ ] Chat widget UI functional (no backend)
- [ ] Email references exist but not configured
- [ ] 5-6 orphaned templates identified
- [ ] Duplicate BrandProfile model found
- [ ] All migrations applied

### Nice-to-Have 🔧
- [ ] Backup files ready for cleanup
- [ ] Old create_superuser.py identified for update
- [ ] Code quality issues documented

---

## ✅ Final Verification

Run this command to generate a full system report:

```bash
python manage.py check
# Should output: System check identified no issues (0 silenced).
```

If you see errors:
1. Check Python version compatibility
2. Verify all dependencies installed
3. Run migrations: `python manage.py migrate`
4. Run seed: `python seed_database.py && python create_test_users.py`

---

**Audit Checklist Version**: 1.0  
**Last Updated**: 2026-06-23
