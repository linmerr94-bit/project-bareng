# BRAND CONSOLIDATION - DIAGRAMS & TROUBLESHOOTING

**Date**: 19 Juni 2026
**Purpose**: Visual guides and detailed troubleshooting

---

## 🗺️ ARCHITECTURE DIAGRAMS

### Current Architecture (Problematic)

```
┌─────────────────────────────────────────────────────────┐
│                    USERS MODEL                          │
│  (id, username, email, role, password_hash, ...)       │
└──┬───────────────────────────────────────┬──────────────┘
   │                                       │
   │ OneToOne (user_id)          OneToOne (user)
   ▼                                       ▼
┌─────────────────────┐          ┌──────────────────────┐
│ BRAND                │          │ BRANDPROFILE         │
│ (master_products)    │          │ (master_brands)      │
├─────────────────────┤          ├──────────────────────┤
│ ✓ brand_id (PK)     │          │ ✗ id (implicit PK)   │
│ ✓ user_id (FK)      │◄────────►│ ✓ user (FK)          │
│ ✓ brand_name        │ Duplicate!│ ✓ brand_name         │
│ ✓ logo              │          │ ✗ NO logo            │
│ ✓ description       │          │ ✗ NO description     │
│ ✓ status            │ Different │ ✓ status (diff fmt)  │
│ ✓ approved_at       │  format!  │ ✗ NO approved_at     │
│ ✓ approved_by       │          │ ✗ NO approved_by     │
│ ✗ NO nib_or_ktp     │          │ ✓ nib_or_ktp         │
│ ✗ NO rating         │          │ ✓ rating             │
└────────────┬────────┘          └──────────────────────┘
             │
      FK (brand_id)
             │
    ┌────────▼─────────┐
    │ PRODUCT          │
    ├──────────────────┤
    │ - product_id (PK)│
    │ - brand_id (FK)  │ ◄──── Product tied to Brand
    │ - category_id    │
    │ - product_name   │
    │ - price          │
    │ - stock          │
    └──────────────────┘

    ┌──────────────────┐
    │ ORDER            │
    ├──────────────────┤
    │ - order_id (PK)  │
    │ - user_id (FK)   │
    │ - brand_id (FK)  │ ◄──── Order tied to Brand
    │ - order_code     │
    │ - total_amount   │
    └──────────────────┘

PROBLEM: 2 Brand sources for same user → Inconsistency!
```

---

### Target Architecture (After Consolidation)

```
┌─────────────────────────────────────────────────────────┐
│                    USERS MODEL                          │
│  (id, username, email, role, password_hash, ...)       │
└──┬───────────────────────────────────────────────────────┘
   │
   │ OneToOne (user_id)
   ▼
┌──────────────────────────────────────┐
│ BRAND (CONSOLIDATED)                 │
│ (master_products/models.py)          │
├──────────────────────────────────────┤
│ ✓ brand_id (PK)                      │
│ ✓ user_id (FK) - OneToOne            │
│ ✓ brand_name                         │
│ ✓ logo                               │
│ ✓ description                        │
│ ✓ status ['pending', 'approved',     │
│           'rejected', 'suspended']   │ ← NEW CHOICE
│ ✓ approved_at                        │
│ ✓ approved_by                        │
│ ✓ nib_or_ktp ◄── MIGRATED from      │
│ ✓ rating ◄── MIGRATED from          │
│              BrandProfile            │
└────────────┬─────────────────────────┘
             │
      FK (brand_id)
             ├─────────────────┐
             ▼                 ▼
    ┌────────────────┐   ┌──────────────┐
    │ PRODUCT        │   │ ORDER        │
    ├────────────────┤   ├──────────────┤
    │ product_id (PK)│   │ order_id (PK)│
    │ brand_id (FK)  │   │ brand_id (FK)│
    │ ...            │   │ ...          │
    └────────────────┘   └──────────────┘

BENEFIT: Single source of truth → Consistency!
REMOVED: BrandProfile (master_brands) - NO LONGER NEEDED
```

---

## 🔄 DATA MIGRATION FLOW

```
┌──────────────────────────────────────────────────────────┐
│               MIGRATION PROCESS                          │
└──────────────────────────────────────────────────────────┘

STEP 1: Schema Change
─────────────────────
Brand Table (BEFORE)
┌─────────────────────────────────────┐
│ brand_id | user_id | brand_name ... │
│ 1        │ 5       │ Tech Store     │
│ 2        │ 6       │ Electronics    │
└─────────────────────────────────────┘

         ADD COLUMNS
              ▼

Brand Table (AFTER Schema Update)
┌──────────────────────────────────────────────────┐
│ brand_id | user_id | brand_name | nib_or_ktp |  │
│ 1        │ 5       │ Tech       │ NULL       │  │
│ 2        │ 6       │ Electro    │ NULL       │  │
│ rating | status  | ...                       │
│ 0.0    │ pending │ ...                       │
│ 0.0    │ pending │ ...                       │
└──────────────────────────────────────────────────┘


STEP 2: Data Migration
──────────────────────
BrandProfile Table (SOURCE)
┌──────────────────────────────────────┐
│ id | user_id | brand_name | nib_or_ │
│ 1  │ 5       │ Tech       │ 123456  │
│ 2  │ 6       │ Electro    │ 234567  │
│ 3  │ 7       │ Gadgets    │ 345678  │
└──────────────────────────────────────┘

     FOR EACH BrandProfile
     IF Brand exists for user:
        UPDATE Brand.nib_or_ktp
        UPDATE Brand.rating
        UPDATE Brand.status
     ELSE:
        CREATE Brand from BrandProfile

         ▼

Brand Table (AFTER Data Migration)
┌──────────────────────────────────────┐
│ brand_id | nib_or_ktp | rating | ... │
│ 1        │ 123456     │ 0.0    │ ... │
│ 2        │ 234567     │ 0.0    │ ... │
│ 3        │ 345678     │ 0.0    │ ... │
└──────────────────────────────────────┘


STEP 3: Deletion
────────────────
BrandProfile Table → DROP (NO LONGER NEEDED)

Result: SINGLE source of truth ✅
```

---

## 📊 STATUS MAPPING

```
BrandProfile Status  →  Brand Status
═════════════════════════════════════

'PENDING'     →  'pending'    (UPPERCASE → lowercase)
'APPROVED'    →  'approved'   (UPPERCASE → lowercase)
'SUSPENDED'   →  'suspended'  (NEW choice added)

VendorRequest Status (for reference)
────────────────────────────────────
'Pending'     →  (not directly mapped to Brand)
'Approved'    →  (not directly mapped to Brand)
'Rejected'    →  'rejected' (in Brand)

Note: VendorRequest is SEPARATE from Brand lifecycle
      (used for initial application, not ongoing status)
```

---

## 🔍 DETAILED TROUBLESHOOTING GUIDE

### Issue 1: Migration Fails: "Duplicate Key Value"

**Symptoms**:
```
psycopg2.IntegrityError: duplicate key value violates unique constraint
```

**Root Causes**:
1. Two BrandProfile records with same nib_or_ktp
2. Trying to insert duplicate nib_or_ktp

**Solutions**:

**Option A: Check for duplicates before migration**
```python
from master_brands.models import BrandProfile
from django.db.models import Count

# Find duplicates
duplicates = BrandProfile.objects.values('nib_or_ktp')\
    .annotate(count=Count('nib_or_ktp'))\
    .filter(count__gt=1)

for dup in duplicates:
    profiles = BrandProfile.objects.filter(nib_or_ktp=dup['nib_or_ktp'])
    print(f"Duplicate NIB: {dup['nib_or_ktp']}")
    for p in profiles:
        print(f"  - {p.brand_name} (user_id: {p.user_id})")
```

**Option B: Fix migration script to handle duplicates**
```python
# In migration, wrap with try-except or use unique_together check
try:
    brand.nib_or_ktp = bp.nib_or_ktp
    brand.save()
except IntegrityError:
    # Skip or merge with existing
    pass
```

**Option C: Merge duplicates**
```python
# Keep one, merge to another
primary = BrandProfile.objects.filter(nib_or_ktp='123456').first()
duplicates = BrandProfile.objects.filter(nib_or_ktp='123456')[1:]

for dup in duplicates:
    # Copy relevant data to primary if needed
    dup.delete()
```

---

### Issue 2: Migration Fails: "No Such Table"

**Symptoms**:
```
django.db.utils.OperationalError: no such table: master_brands_brandprofile
```

**Root Causes**:
1. Trying to access BrandProfile before it's created
2. Migration order issue
3. Previous migration deleted table prematurely

**Solutions**:

**Option A: Check migration dependencies**
```bash
python manage.py migrate --plan
# Verify order: should create BrandProfile before accessing it
```

**Option B: Rollback and retry**
```bash
python manage.py migrate master_brands zero
python manage.py migrate master_brands 0001
python manage.py migrate master_products 0002
```

**Option C: Manual SQL check**
```bash
python manage.py dbshell
.tables
# Verify master_brands_brandprofile exists

.schema master_brands_brandprofile
# Check structure
```

---

### Issue 3: Foreign Key Constraint Fails

**Symptoms**:
```
IntegrityError: FOREIGN KEY constraint failed
```

**Root Causes**:
1. Product.brand_id references non-existent Brand
2. Order.brand_id references non-existent Brand
3. Orphaned product/order records

**Solutions**:

**Option A: Find orphaned records**
```python
from master_products.models import Product, Order, Brand

# Find orphaned products
orphaned_products = Product.objects.filter(brand_id__isnull=True)
print(f"Orphaned products: {orphaned_products.count()}")

# Find orphaned orders
orphaned_orders = Order.objects.filter(brand_id__isnull=True)
print(f"Orphaned orders: {orphaned_orders.count()}")

# Fix: Assign to a default brand or delete
for product in orphaned_products:
    product.brand_id = Brand.objects.first()  # or handle as needed
    product.save()
```

**Option B: Check referential integrity**
```bash
python manage.py dbshell
.mode line

# Check for orphaned products
SELECT p.product_id, p.brand_id FROM products p
LEFT JOIN brands b ON p.brand_id = b.brand_id
WHERE b.brand_id IS NULL;

# Check for orphaned orders
SELECT o.order_id, o.brand_id FROM orders o
LEFT JOIN brands b ON o.brand_id = b.brand_id
WHERE b.brand_id IS NULL;
```

---

### Issue 4: Admin Interface Shows Error

**Symptoms**:
```
FieldError: Unknown field(s) (nib_or_ktp) specified in list_display
```

**Root Causes**:
1. admin.py updated before migration runs
2. Typo in field name
3. Field not properly defined in model

**Solutions**:

**Option A: Verify migration applied**
```bash
python manage.py migrate --plan
python manage.py showmigrations master_products
# Check if 0002_add_nib_rating_to_brand is marked [X]
```

**Option B: Check field actually exists**
```bash
python manage.py shell
from master_products.models import Brand
Brand._meta.get_field('nib_or_ktp')  # Should work if field exists
```

**Option C: Sync database schema**
```bash
python manage.py migrate
python manage.py migrate --run-syncdb  # Emergency sync (use with caution)
```

---

### Issue 5: Status Values Don't Match

**Symptoms**:
```
Brand.status = 'PENDING'  # Uppercase after migration
Expected: 'pending'       # Lowercase
```

**Root Causes**:
1. Data migration script didn't normalize status
2. Old records not updated
3. Script has case-sensitivity bug

**Solutions**:

**Option A: Fix in migration script**
```python
# Update migration 0003 to normalize:
if bp.status == 'PENDING':
    brand.status = 'pending'  # ← Ensure lowercase
elif bp.status == 'APPROVED':
    brand.status = 'approved'
```

**Option B: Manual fix after migration**
```python
from master_products.models import Brand

# Find all uppercase statuses
bad_brands = Brand.objects.filter(status__in=['PENDING', 'APPROVED', 'SUSPENDED'])
for brand in bad_brands:
    brand.status = brand.status.lower()
    brand.save()
```

**Option C: SQL fix**
```sql
UPDATE brands SET status = LOWER(status) 
WHERE status IN ('PENDING', 'APPROVED', 'SUSPENDED');
```

---

### Issue 6: Data Loss After Migration

**Symptoms**:
```
Before: 10 BrandProfile records
After: 5 Brand records
Missing data!
```

**Root Causes**:
1. Migration script has bugs
2. Foreign key conflicts
3. Duplicate key violations
4. Error during migration (partial execution)

**Solutions**:

**Option A: Check backup for data**
```bash
# Restore from backup
cp db_backup_20260619_HHMMSS.sqlite3 db.sqlite3

# Re-run migration with fixes
```

**Option B: Analyze what happened**
```python
# Check migration logs
python manage.py migrate --plan --verbose

# Look for error messages
cat logs/migration.log
```

**Option C: Reverse and retry**
```bash
# Rollback
python manage.py migrate master_products 0001
python manage.py migrate master_brands zero

# Fix migration script
# Re-run
```

---

## ✅ VERIFICATION STEPS

### Step 1: Database Level Verification

```sql
-- 1. Check table structure
.schema brands

-- 2. Verify columns exist
PRAGMA table_info(brands);
-- Should show: nib_or_ktp, rating columns

-- 3. Check data integrity
SELECT COUNT(*) as total_brands,
       COUNT(DISTINCT user_id) as unique_users,
       COUNT(CASE WHEN nib_or_ktp IS NOT NULL THEN 1 END) as with_nib,
       COUNT(CASE WHEN rating > 0 THEN 1 END) as with_rating
FROM brands;

-- 4. Check for duplicates
SELECT user_id, COUNT(*) 
FROM brands 
GROUP BY user_id 
HAVING COUNT(*) > 1;
-- Should return nothing (OneToOne constraint)

-- 5. Verify no orphaned records
SELECT COUNT(*) FROM products WHERE brand_id NOT IN (SELECT brand_id FROM brands);
SELECT COUNT(*) FROM orders WHERE brand_id NOT IN (SELECT brand_id FROM brands);
-- Both should return 0

-- 6. Check status values
SELECT DISTINCT status FROM brands;
-- Should be: ['pending', 'approved', 'rejected', 'suspended']
```

### Step 2: Django ORM Verification

```python
from master_products.models import Brand, Product, Order

# 1. Check model works
brands = Brand.objects.all()
print(f"Total brands: {brands.count()}")

# 2. Check new fields
for brand in brands[:3]:
    print(f"{brand.brand_name}: nib={brand.nib_or_ktp}, rating={brand.rating}")

# 3. Check relationships
products_with_brand = Product.objects.select_related('brand_id').filter(brand_id__isnull=False)
print(f"Products with brand: {products_with_brand.count()}")

# 4. Check orders
orders_with_brand = Order.objects.select_related('brand_id').filter(brand_id__isnull=False)
print(f"Orders with brand: {orders_with_brand.count()}")

# 5. Check OneToOne constraint (user can't have multiple brands)
from django.db.models import Count
duplicate_users = Brand.objects.values('user_id').annotate(count=Count('user_id')).filter(count__gt=1)
print(f"Users with multiple brands: {duplicate_users.count()}")  # Should be 0
```

### Step 3: Admin Interface Verification

```
1. Go to: http://127.0.0.1:8000/admin/master_products/brand/
2. Check:
   □ Page loads without error
   □ nib_or_ktp column visible in list
   □ rating column visible in list
   □ status dropdown has 4 choices (including 'suspended')
3. Edit a brand:
   □ Can see all fields
   □ nib_or_ktp field visible
   □ rating field visible
   □ Can save without error
```

### Step 4: Workflow Verification

```
1. Test Add Product:
   □ Login as vendor
   □ Go to /vendor/add-product/
   □ Add product
   □ Check: Uses Brand (not BrandProfile)
   □ Product appears with correct brand

2. Test Checkout:
   □ Browse products
   □ Add to cart
   □ Checkout
   □ Create order
   □ Check: Order has correct brand_id

3. Test Order Details:
   □ View order detail
   □ Brand info displays correctly
   □ No errors in console
```

---

## 🚨 EMERGENCY PROCEDURES

### Complete Rollback

**If migration is broken and data is corrupted:**

```bash
# Step 1: Stop server
# Ctrl+C or systemctl stop django

# Step 2: Find clean backup
ls -la db_backup_*.sqlite3
ls -la db_migration_failed_*.sqlite3

# Step 3: Identify which to use
# Use most recent BACKUP from BEFORE migration
cp db_backup_20260619_BEFORE.sqlite3 db.sqlite3

# Step 4: Rollback all migrations
python manage.py migrate master_products 0001
python manage.py migrate master_brands zero

# Step 5: Delete problematic migrations
cd master_products/migrations
rm 0002_*.py 0003_*.py
cd ../..

cd master_brands/migrations
rm 0001_*.py
cd ../..

# Step 6: Restart server
python manage.py runserver

# Step 7: Investigate and fix
# Review code changes
# Fix migration scripts
# Try again
```

---

**Status**: COMPREHENSIVE TROUBLESHOOTING GUIDE
**Date**: 19 Juni 2026
**Covers**: 6 common issues + 5 verification steps + emergency procedures

