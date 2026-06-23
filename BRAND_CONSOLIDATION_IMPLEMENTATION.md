# BRAND CONSOLIDATION - IMPLEMENTATION GUIDE

**Status**: Step-by-step execution guide with ready-to-use code
**Date**: 19 Juni 2026
**Effort**: ~2 hours from start to finish

---

## 🎯 OVERVIEW

This guide provides exact code changes and commands to consolidate `BrandProfile` into `Brand` model.

**Before**: 2 models (Brand + BrandProfile)
**After**: 1 model (Brand) with all features

---

## 📋 STEP 1: Update master_products/models.py

### Location: Line 10-100 (Brand class definition)

### ACTION: Add imports at top of file

**Find** (line 1-5):
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
```

**Change to** (add MaxValueValidator if not present):
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
```
✅ (No change needed if already imported)

### ACTION: Update Brand.STATUS_CHOICES

**Find** (around line 15-21):
```python
    # Pilihan status brand
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
```

**Change to**:
```python
    # Pilihan status brand
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
```

### ACTION: Add new fields to Brand model

**Find** (around line 75-80, after `approved_by` field):
```python
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_brands',
        db_column='approved_by',
        help_text="Admin yang menyetujui brand ini"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
```

**Change to** (insert new fields BEFORE `created_at`):
```python
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
```

---

## 📋 STEP 2: Update master_products/views.py

### Location: Line 17 and Line 608

### ACTION: Remove BrandProfile import

**Find** (line 15-20):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from master_brands.models import BrandProfile
```

**Change to** (delete line with BrandProfile):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
# Removed: from master_brands.models import BrandProfile
```

### ACTION: Update add_product_view function

**Find** (around line 600-620):
```python
    # Vendor harus memiliki BrandProfile untuk menambah produk
    brand_profile, created = BrandProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'brand_name': request.user.username
        }
    )
    
    if not brand_profile.status == 'APPROVED':
        messages.warning(request, '⚠️ Anda belum disetujui sebagai brand/vendor!')
        return redirect('master_products:product_list')
    
    # Generate SKU dari brand name
    sku = f"{brand_profile.brand_name[:3].upper()}_{name[:5].upper()}_{int(time.time())}"
    
    # Create product
    product = Product.objects.create(
        brand_id=brand_profile,
```

**Change to**:
```python
    # Vendor harus memiliki Brand untuk menambah produk
    brand, created = Brand.objects.get_or_create(
        user_id=request.user,
        defaults={
            'brand_name': request.user.username
        }
    )
    
    if not brand.status == 'approved':  # Changed to lowercase
        messages.warning(request, '⚠️ Anda belum disetujui sebagai brand/vendor!')
        return redirect('master_products:product_list')
    
    # Generate SKU dari brand name
    sku = f"{brand.brand_name[:3].upper()}_{name[:5].upper()}_{int(time.time())}"
    
    # Create product
    product = Product.objects.create(
        brand_id=brand,
```

---

## 📋 STEP 3: Update master_products/admin.py

### Location: BrandAdmin class (around line 16-30)

### ACTION: Update list_display

**Find** (around line 22):
```python
    list_display = (
        'brand_id', 'brand_name', 'user_id', 'status_badge', 'created_at'
    )
```

**Change to**:
```python
    list_display = (
        'brand_id', 'brand_name', 'user_id', 'nib_or_ktp', 'rating', 
        'status_badge', 'created_at'
    )
```

### ACTION: Update fieldsets

**Find** (around line 25-32):
```python
    fieldsets = (
        (_('Brand Information'), {
            'fields': ('user_id', 'brand_name', 'logo', 'description')
        }),
        (_('Approval Status'), {
            'fields': ('status', 'approved_at', 'approved_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

**Change to**:
```python
    fieldsets = (
        (_('Brand Information'), {
            'fields': ('user_id', 'brand_name', 'logo', 'description', 'nib_or_ktp')
        }),
        (_('Performance Metrics'), {
            'fields': ('rating',)
        }),
        (_('Approval Status'), {
            'fields': ('status', 'approved_at', 'approved_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

### ACTION: Add readonly_fields

**Find** (around line 24):
```python
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
```

**Change to** (add 'rating' since auto-computed):
```python
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'rating')
```

---

## 📋 STEP 4: Delete BrandProfile from master_brands/models.py

### Location: Entire file

### ACTION: Replace entire content

**Find**: Entire file content starting with BrandProfile class

**Change to**:
```python
# Brand models have been consolidated into master_products.models.Brand
# This file is now deprecated and kept for reference only.
# See: BRAND_CONSOLIDATION_ANALYSIS.md for migration details.
```

---

## 📋 STEP 5: Update master_brands/admin.py

### Location: Entire file

### ACTION: Clear BrandProfile registration

**Find**:
```python
from django.contrib import admin
from .models import BrandProfile

@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    """Admin interface untuk BrandProfile"""
    ...
```

**Change to**:
```python
from django.contrib import admin

# Brand models consolidated into master_products app
# See: master_products.admin.BrandAdmin for Brand admin interface
```

---

## 🚀 STEP 6: Create Migrations

### Command 1: Create schema migration for new fields

```bash
cd d:\PROJEK UAS E-COMMERCE
python manage.py makemigrations master_products
```

**Expected output**:
```
Migrations for 'master_products':
  master_products/migrations/0002_add_nib_rating_to_brand.py
    - Add field nib_or_ktp to brand
    - Add field rating to brand
    - Alter field status on brand
```

### Command 2: Create data migration

```bash
python manage.py makemigrations master_products --empty --name migrate_brandprofile_to_brand
```

**Expected output**:
```
Migrations for 'master_products':
  master_products/migrations/0003_migrate_brandprofile_to_brand.py
```

### Command 3: Edit data migration file

**File**: `master_products/migrations/0003_migrate_brandprofile_to_brand.py`

**Replace entire content with**:
```python
from django.db import migrations

def migrate_brandprofile_to_brand(apps, schema_editor):
    """
    Migrate data dari BrandProfile (master_brands) ke Brand (master_products)
    """
    Brand = apps.get_model('master_products', 'Brand')
    
    try:
        # Import BrandProfile from apps
        BrandProfile = apps.get_model('master_brands', 'BrandProfile')
        
        migrated_count = 0
        duplicates = 0
        
        for bp in BrandProfile.objects.all():
            try:
                # Check if Brand sudah ada untuk user ini
                brand = Brand.objects.get(user_id=bp.user)
                
                # Update existing Brand
                brand.nib_or_ktp = bp.nib_or_ktp
                brand.rating = bp.rating
                
                # Map status dari BrandProfile ke Brand
                if bp.status == 'PENDING':
                    brand.status = 'pending'
                elif bp.status == 'APPROVED':
                    brand.status = 'approved'
                elif bp.status == 'SUSPENDED':
                    brand.status = 'suspended'
                
                brand.save()
                duplicates += 1
                print(f"Updated Brand: {brand.brand_name}")
                
            except Brand.DoesNotExist:
                # Create new Brand dari BrandProfile
                brand = Brand(
                    user_id=bp.user,
                    brand_name=bp.brand_name,
                    nib_or_ktp=bp.nib_or_ktp,
                    rating=bp.rating,
                    created_at=bp.created_at,
                    updated_at=bp.updated_at,
                )
                
                # Map status
                if bp.status == 'PENDING':
                    brand.status = 'pending'
                elif bp.status == 'APPROVED':
                    brand.status = 'approved'
                elif bp.status == 'SUSPENDED':
                    brand.status = 'suspended'
                
                brand.save()
                migrated_count += 1
                print(f"Migrated Brand: {brand.brand_name}")
        
        print(f"\n=== MIGRATION SUMMARY ===")
        print(f"New Brands created: {migrated_count}")
        print(f"Existing Brands updated: {duplicates}")
        print(f"Total BrandProfile processed: {BrandProfile.objects.count()}")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()

def reverse_migrate(apps, schema_editor):
    """
    Rollback: Clear nib_or_ktp dan rating dari Brand
    (Jangan delete Brand records karena sudah digunakan)
    """
    Brand = apps.get_model('master_products', 'Brand')
    Brand.objects.all().update(nib_or_ktp=None, rating=0.0)
    print("Rollback complete: nib_or_ktp dan rating cleared")

class Migration(migrations.Migration):

    dependencies = [
        ('master_products', '0002_add_nib_rating_to_brand'),  # Sesuaikan dengan nomor migration sebelumnya
    ]

    operations = [
        migrations.RunPython(migrate_brandprofile_to_brand, reverse_migrate),
    ]
```

### Command 4: Create deletion migration untuk BrandProfile

```bash
python manage.py makemigrations master_brands
```

**Expected output**:
```
Migrations for 'master_brands':
  master_brands/migrations/0001_delete_brandprofile.py
    - Delete model BrandProfile
```

---

## ✅ STEP 7: Apply Migrations

### Command 1: Preview migrations

```bash
python manage.py migrate --plan
```

**Expected output**:
```
Planned operations:
  master_products:0002 - Add field nib_or_ktp to brand
  master_products:0002 - Add field rating to brand
  master_products:0002 - Alter field status on brand
  master_products:0003 - Raw SQL operation (migrate_brandprofile_to_brand)
  master_brands:0001 - Delete model BrandProfile
```

### Command 2: Apply migrations

```bash
python manage.py migrate
```

**Expected output**:
```
Operations to perform:
  Apply all migrations: users, brands, master_brands, master_products
Running migrations:
  Rendering model states... DONE
  Applying master_products.0002_add_nib_rating_to_brand... OK
  Applying master_products.0003_migrate_brandprofile_to_brand... OK
  Applying master_brands.0001_delete_brandprofile... OK
```

---

## 🧪 STEP 8: Verification Commands

### Command 1: Database check

```bash
python manage.py check
```

**Expected**: ✅ All checks passed

### Command 2: Verify data migration via shell

```bash
python manage.py shell
```

```python
# Test 1: BrandProfile should not exist
from master_brands.models import BrandProfile
print("Should error:")
BrandProfile.objects.all()  # ❌ No such table

# Test 2: Brand should have new fields
from master_products.models import Brand
brands = Brand.objects.all()
print(f"\n✅ Total Brands: {brands.count()}")

for brand in brands[:3]:
    print(f"\nBrand: {brand.brand_name}")
    print(f"  User: {brand.user_id.username}")
    print(f"  NIB: {brand.nib_or_ktp}")
    print(f"  Rating: {brand.rating}")
    print(f"  Status: {brand.status}")

# Test 3: Product relations still work
from master_products.models import Product
products = Product.objects.select_related('brand_id').filter(is_active=True)[:3]
print(f"\n✅ Sample Products:")
for p in products:
    print(f"  {p.product_name} → {p.brand_id.brand_name}")

# Test 4: Order relations still work
from master_products.models import Order
orders = Order.objects.select_related('brand_id').all()[:3]
print(f"\n✅ Sample Orders:")
for o in orders:
    print(f"  Order {o.order_code} → {o.brand_id.brand_name}")

exit()
```

### Command 3: Admin interface check

```bash
python manage.py runserver
# Navigate to: http://127.0.0.1:8000/admin/master_products/brand/
# Verify: New columns (nib_or_ktp, rating) appear
```

### Command 4: Check database directly

```bash
# SQLite shell
python manage.py dbshell
```

```sql
-- Check 1: Brand table structure
.schema brands

-- Check 2: Verify data migrated
SELECT COUNT(*) as total_brands FROM brands;

-- Check 3: Check nib_or_ktp values
SELECT brand_name, nib_or_ktp, rating, status FROM brands LIMIT 5;

-- Check 4: No orphaned BrandProfile
SELECT COUNT(*) as orphaned FROM sqlite_master WHERE type='table' AND name='master_brands_brandprofile';
-- Should return: 0

.exit
```

---

## 🔄 TESTING CHECKLIST

After migration, test these scenarios:

### Test 1: Admin Interface
```
□ Go to /admin/master_products/brand/
□ See nib_or_ktp column
□ See rating column
□ Can edit brand
□ Can see all fields in form
```

### Test 2: Add Product (Vendor)
```
□ Login as vendor
□ Go to /vendor/add-product/
□ Add product
□ Should work (uses Brand, not BrandProfile)
□ Product shows correct brand
```

### Test 3: Product List
```
□ Go to /
□ See all products
□ Click product
□ See brand info (from Brand model, not BrandProfile)
```

### Test 4: Checkout & Order
```
□ Add product to cart
□ Checkout
□ Create order
□ Order shows brand name correctly
□ View order history
□ View order detail
```

### Test 5: API/Queries
```python
# In Django shell:

# Should work
from master_products.models import Brand, Product, Order
Product.objects.filter(brand_id__status='approved').count()
Order.objects.filter(brand_id__rating__gte=4.0).count()

# Should NOT work (BrandProfile deleted)
from master_brands.models import BrandProfile
# ❌ ImportError: cannot import name 'BrandProfile'
```

---

## ⏮️ ROLLBACK PROCEDURE (if needed)

### Rollback to before consolidation

```bash
# Rollback last 3 migrations
python manage.py migrate master_products 0001
python manage.py migrate master_brands zero

# Or specific:
python manage.py migrate master_products 0001  # Back to before changes
```

### Restore from backup (if migrations fail)

```bash
# Stop server
# Copy backup database
cp db.sqlite3.backup db.sqlite3
# Restart server
python manage.py runserver
```

---

## 📊 SUMMARY OF CHANGES

| Component | Before | After | Impact |
|-----------|--------|-------|--------|
| **Models** | 2 (Brand + BrandProfile) | 1 (Brand) | Cleaner architecture |
| **Files** | 2 models + admin + views | 1 model + admin + views | Simpler code |
| **Database** | 2 tables | 1 table | Less complexity |
| **Fields** | Status 3 choices | Status 4 choices | More flexibility |
| **Data** | Potentially split | Unified | Better consistency |
| **Lines Changed** | ~150 | - | Small refactor |

---

## ✅ COMPLETION CHECKLIST

After all steps complete:

```
□ models.py updated (Brand fields added)
□ views.py updated (BrandProfile → Brand)
□ admin.py updated (fields in list_display & fieldsets)
□ master_brands/models.py cleared
□ master_brands/admin.py cleared
□ Migrations created (3 files)
□ Data migration file edited manually
□ Migrations applied (python manage.py migrate)
□ Database check passed
□ Verification commands executed
□ All tests passed
□ Admin interface shows new columns
□ Add product workflow works
□ Checkout workflow works
□ Order tracking works
□ No errors in Django logs
□ Backup database saved
```

---

## 📞 COMMON ISSUES & SOLUTIONS

### Issue 1: Migration fails with "no such table"

**Cause**: BrandProfile referenced before deletion

**Solution**:
```bash
python manage.py migrate master_products 0002  # Skip data migration
python manage.py migrate master_brands 0001    # Delete table
python manage.py migrate master_products 0003  # Now apply data migration
```

### Issue 2: "duplicate key value violates unique constraint"

**Cause**: nib_or_ktp already exists

**Solution**: In migration, wrap in try/except or update existing

### Issue 3: "no brand found for user"

**Cause**: Legacy data issue

**Solution**: Update migration to use `get_or_create` (already done)

### Issue 4: Admin page shows error

**Cause**: readonly_fields reference missing column

**Solution**: Check admin.py readonly_fields

---

**Status**: ✅ READY FOR IMPLEMENTATION
**Effort**: ~2-3 hours
**Risk**: Low (with backup)
**Date**: 19 Juni 2026

