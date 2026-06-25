# BRAND CONSOLIDATION - READY-TO-USE SCRIPTS

**Date**: 19 Juni 2026
**Purpose**: Quick reference for migration scripts and SQL commands
**Format**: Copy-paste ready

---

## 🔧 SCRIPT 1: Pre-Migration Backup

**File**: `backup_before_consolidation.py`

**Location**: Project root (d:\PROJEK UAS E-COMMERCE\)

**Usage**: 
```bash
python backup_before_consolidation.py
```

```python
import shutil
import os
from datetime import datetime

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_name = f"db_backup_{timestamp}.sqlite3"

try:
    shutil.copy('db.sqlite3', backup_name)
    print(f"✅ Database backed up to: {backup_name}")
    
    # Also backup migration files
    shutil.copytree('master_products/migrations', 
                    f'migrations_backup_{timestamp}', 
                    dirs_exist_ok=True)
    print(f"✅ Migrations backed up to: migrations_backup_{timestamp}/")
    
    # List backups
    backups = [f for f in os.listdir('.') if f.startswith('db_backup_')]
    print(f"\n📦 Available backups: {len(backups)}")
    for backup in sorted(backups)[-3:]:
        size_mb = os.path.getsize(backup) / (1024*1024)
        print(f"  - {backup} ({size_mb:.2f} MB)")
        
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 🔧 SCRIPT 2: Verify Data Integrity (Pre-Migration)

**File**: `verify_data_before_migration.py`

**Location**: Project root

**Usage**:
```bash
python manage.py shell < verify_data_before_migration.py
```

```python
#!/usr/bin/env python
"""
Verify data integrity before Brand consolidation migration
"""

print("=" * 60)
print("BRAND CONSOLIDATION - PRE-MIGRATION VERIFICATION")
print("=" * 60)

try:
    from master_products.models import Brand, Product, Order, OrderItem
    from master_brands.models import BrandProfile
    from users.models import User
    
    # Test 1: Count existing records
    print("\n1️⃣  EXISTING DATA COUNTS:")
    print(f"   Brands:        {Brand.objects.count()}")
    print(f"   BrandProfile:  {BrandProfile.objects.count()}")
    print(f"   Products:      {Product.objects.count()}")
    print(f"   Orders:        {Order.objects.count()}")
    print(f"   Users:         {User.objects.count()}")
    
    # Test 2: Check for orphaned records
    print("\n2️⃣  ORPHANED RECORDS CHECK:")
    
    orphaned_products = Product.objects.filter(brand_id__isnull=True).count()
    print(f"   Products without Brand: {orphaned_products}")
    
    orphaned_orders = Order.objects.filter(brand_id__isnull=True).count()
    print(f"   Orders without Brand: {orphaned_orders}")
    
    # Test 3: Check user-brand relationships
    print("\n3️⃣  USER-BRAND RELATIONSHIP:")
    
    brand_users = Brand.objects.values_list('user_id', flat=True).distinct()
    print(f"   Users with Brand: {brand_users.count()}")
    
    try:
        profile_users = BrandProfile.objects.values_list('user', flat=True).distinct()
        print(f"   Users with BrandProfile: {profile_users.count()}")
        
        # Check overlap
        overlap = set(brand_users) & set(profile_users)
        print(f"   Users in BOTH: {len(overlap)}")
        
        if overlap:
            print(f"\n   ⚠️  WARNING: {len(overlap)} users appear in both Brand and BrandProfile!")
            print("   These will be merged during migration.")
    except:
        print(f"   Users with BrandProfile: (table doesn't exist)")
    
    # Test 4: Check data consistency
    print("\n4️⃣  DATA CONSISTENCY:")
    
    for brand in Brand.objects.all()[:5]:
        products = brand.products.count()
        orders = brand.orders.count()
        status = brand.status
        print(f"   {brand.brand_name}: {products} products, {orders} orders, status={status}")
    
    # Test 5: Check status values
    print("\n5️⃣  STATUS VALUE CHECK:")
    
    brand_statuses = Brand.objects.values('status').distinct()
    print(f"   Brand statuses: {[s['status'] for s in brand_statuses]}")
    
    try:
        profile_statuses = BrandProfile.objects.values('status').distinct()
        print(f"   BrandProfile statuses: {[s['status'] for s in profile_statuses]}")
    except:
        pass
    
    print("\n✅ PRE-MIGRATION VERIFICATION COMPLETE")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
```

---

## 🔧 SCRIPT 3: Post-Migration Verification

**File**: `verify_data_after_migration.py`

**Location**: Project root

**Usage**:
```bash
python manage.py shell < verify_data_after_migration.py
```

```python
#!/usr/bin/env python
"""
Verify data integrity after Brand consolidation migration
"""

print("=" * 60)
print("BRAND CONSOLIDATION - POST-MIGRATION VERIFICATION")
print("=" * 60)

try:
    from master_products.models import Brand, Product, Order, OrderItem
    from master_brands.models import BrandProfile
    from django.db import connection
    
    # Test 1: Verify BrandProfile is deleted
    print("\n1️⃣  VERIFY BRANDPROFILE DELETION:")
    
    try:
        count = BrandProfile.objects.count()
        print(f"   ❌ BrandProfile still exists! Count: {count}")
    except Exception as e:
        print(f"   ✅ BrandProfile successfully deleted")
    
    # Test 2: Check new fields exist
    print("\n2️⃣  VERIFY NEW FIELDS:")
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(brands)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_fields = ['nib_or_ktp', 'rating']
        for field in required_fields:
            if field in columns:
                print(f"   ✅ {field} field exists")
            else:
                print(f"   ❌ {field} field MISSING")
    
    # Test 3: Check data migration
    print("\n3️⃣  VERIFY DATA MIGRATION:")
    
    brands_with_nib = Brand.objects.exclude(nib_or_ktp__isnull=True).exclude(nib_or_ktp='').count()
    print(f"   Brands with nib_or_ktp: {brands_with_nib}")
    
    brands_with_rating = Brand.objects.exclude(rating=0.0).count()
    print(f"   Brands with rating > 0: {brands_with_rating}")
    
    # Test 4: Check status values normalized
    print("\n4️⃣  VERIFY STATUS NORMALIZATION:")
    
    brand_statuses = Brand.objects.values('status').distinct()
    statuses = [s['status'] for s in brand_statuses]
    print(f"   Brand statuses: {statuses}")
    
    valid_statuses = ['pending', 'approved', 'rejected', 'suspended']
    for status in statuses:
        if status in valid_statuses:
            print(f"   ✅ {status} is valid")
        else:
            print(f"   ❌ {status} is INVALID")
    
    # Test 5: Verify relationships still work
    print("\n5️⃣  VERIFY RELATIONSHIPS:")
    
    sample_products = Product.objects.select_related('brand_id')[:3]
    for product in sample_products:
        if product.brand_id:
            print(f"   ✅ Product '{product.product_name}' → Brand '{product.brand_id.brand_name}'")
        else:
            print(f"   ❌ Product '{product.product_name}' has NO BRAND!")
    
    sample_orders = Order.objects.select_related('brand_id')[:3]
    for order in sample_orders:
        if order.brand_id:
            print(f"   ✅ Order {order.order_code} → Brand '{order.brand_id.brand_name}'")
        else:
            print(f"   ❌ Order {order.order_code} has NO BRAND!")
    
    # Test 6: Admin interface check
    print("\n6️⃣  ADMIN INTERFACE TEST:")
    
    from django.contrib.admin import site
    from master_products.admin import BrandAdmin
    
    brand_admin = site._registry.get(Brand)
    if brand_admin:
        print(f"   ✅ Brand registered in admin")
        
        list_display = brand_admin.list_display
        if 'nib_or_ktp' in list_display:
            print(f"   ✅ nib_or_ktp in list_display")
        if 'rating' in list_display:
            print(f"   ✅ rating in list_display")
    else:
        print(f"   ❌ Brand NOT registered in admin")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ POST-MIGRATION VERIFICATION COMPLETE")
    print("=" * 60)
    
    # Statistics
    print(f"\nFinal Statistics:")
    print(f"  Total Brands: {Brand.objects.count()}")
    print(f"  Total Products: {Product.objects.count()}")
    print(f"  Total Orders: {Order.objects.count()}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
```

---

## 🔧 SCRIPT 4: Quick Migration Script

**File**: `run_brand_consolidation.py`

**Location**: Project root

**Usage**:
```bash
python run_brand_consolidation.py
```

```python
#!/usr/bin/env python
"""
Automated Brand consolidation migration
Run this after code changes and manual migration files are in place
"""

import os
import sys
import django
from django.core.management import call_command
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

print("=" * 70)
print("AUTOMATED BRAND CONSOLIDATION MIGRATION")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    # Step 1: Create backup
    print("\n[1/5] Creating database backup...")
    call_command('shell', stdin="""
import shutil
shutil.copy('db.sqlite3', f'db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3')
print("  ✅ Backup created")
""")
    
    # Step 2: Check migrations
    print("\n[2/5] Checking migrations...")
    call_command('migrate', '--plan', verbosity=0)
    
    # Step 3: Run migrations
    print("\n[3/5] Running migrations...")
    call_command('migrate', verbosity=1)
    
    # Step 4: Verify data
    print("\n[4/5] Verifying migration...")
    call_command('shell', stdin=open('verify_data_after_migration.py').read())
    
    # Step 5: Check system
    print("\n[5/5] Running system checks...")
    call_command('check')
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext steps:")
    print("  1. Test add product workflow")
    print("  2. Test checkout flow")
    print("  3. Verify admin interface")
    
except Exception as e:
    print(f"\n❌ MIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n⚠️  ROLLBACK INSTRUCTIONS:")
    print("  1. Stop Django server")
    print("  2. Restore from backup: cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3")
    print("  3. Rollback migrations: python manage.py migrate master_products 0001")
    print("  4. Restart server")
    
    sys.exit(1)
```

---

## 🗄️ SQL SCRIPT: Direct Database Migration (Emergency)

**File**: `emergency_brand_consolidation.sql`

**Purpose**: Emergency consolidation if Django migrations fail

**Usage**:
```bash
# SQLite
python manage.py dbshell < emergency_brand_consolidation.sql

# Or manual:
sqlite3 db.sqlite3
sqlite> .read emergency_brand_consolidation.sql
```

```sql
-- EMERGENCY BRAND CONSOLIDATION SQL SCRIPT
-- Only use if Django migrations fail!

-- Step 1: Backup original tables
CREATE TABLE brands_backup AS SELECT * FROM brands;
CREATE TABLE master_brands_brandprofile_backup AS SELECT * FROM master_brands_brandprofile;

-- Step 2: Add new columns to brands table
ALTER TABLE brands ADD COLUMN nib_or_ktp VARCHAR(50) UNIQUE;
ALTER TABLE brands ADD COLUMN rating FLOAT DEFAULT 0.0;

-- Step 3: Migrate data from BrandProfile to Brand
UPDATE brands SET 
    nib_or_ktp = (
        SELECT nib_or_ktp FROM master_brands_brandprofile 
        WHERE master_brands_brandprofile.user_id = brands.user_id
        LIMIT 1
    ),
    rating = (
        SELECT rating FROM master_brands_brandprofile 
        WHERE master_brands_brandprofile.user_id = brands.user_id
        LIMIT 1
    )
WHERE EXISTS (
    SELECT 1 FROM master_brands_brandprofile 
    WHERE master_brands_brandprofile.user_id = brands.user_id
);

-- Step 4: Normalize status (UPPERCASE → lowercase)
UPDATE brands SET status = 'pending' WHERE status = 'PENDING';
UPDATE brands SET status = 'approved' WHERE status = 'APPROVED';
UPDATE brands SET status = 'rejected' WHERE status = 'REJECTED';
UPDATE brands SET status = 'suspended' WHERE status = 'SUSPENDED';

-- Step 5: Verify migration
SELECT COUNT(*) as total_brands FROM brands;
SELECT COUNT(*) as brands_with_nib FROM brands WHERE nib_or_ktp IS NOT NULL;
SELECT COUNT(*) as brands_with_rating FROM brands WHERE rating > 0;

-- Step 6: Check for issues
SELECT brand_name, nib_or_ktp, rating, status FROM brands LIMIT 10;

-- Step 7: Delete BrandProfile table (after verification)
-- DROP TABLE master_brands_brandprofile;
-- ⚠️  Uncomment only after verification!
```

---

## 📊 SCRIPT 5: Data Analysis Before & After

**File**: `analyze_brand_data.py`

**Location**: Project root

**Usage**:
```bash
python manage.py shell < analyze_brand_data.py
```

```python
#!/usr/bin/env python
"""
Analyze Brand data for migration impact assessment
"""

from master_products.models import Brand, Product, Order
from master_brands.models import BrandProfile
from django.db.models import Count, Avg, Q
import json

print("\n" + "=" * 60)
print("BRAND CONSOLIDATION DATA ANALYSIS")
print("=" * 60)

# Analysis 1: Brand distribution
print("\n📊 ANALYSIS 1: Brand Distribution")

brand_stats = Brand.objects.annotate(
    product_count=Count('products'),
    order_count=Count('orders')
).order_by('-product_count')

print(f"\nTotal Brands: {Brand.objects.count()}")
print(f"Brands with products: {Brand.objects.filter(products__isnull=False).distinct().count()}")
print(f"Brands with orders: {Brand.objects.filter(orders__isnull=False).distinct().count()}")

print("\nTop 5 Brands by Product Count:")
for i, brand in enumerate(brand_stats[:5], 1):
    print(f"  {i}. {brand.brand_name}: {brand.product_count} products, {brand.order_count} orders")

# Analysis 2: Status distribution
print("\n📊 ANALYSIS 2: Status Distribution")

status_counts = Brand.objects.values('status').annotate(count=Count('status'))
for status in status_counts:
    print(f"  {status['status']}: {status['count']} brands")

# Analysis 3: BrandProfile data (before deletion)
print("\n📊 ANALYSIS 3: BrandProfile Data (Before Consolidation)")

try:
    bp_count = BrandProfile.objects.count()
    print(f"Total BrandProfile records: {bp_count}")
    
    bp_statuses = BrandProfile.objects.values('status').annotate(count=Count('status'))
    for status in bp_statuses:
        print(f"  {status['status']}: {status['count']}")
    
    # Check for duplicates (users in both Brand and BrandProfile)
    brand_user_ids = set(Brand.objects.values_list('user_id', flat=True))
    bp_user_ids = set(BrandProfile.objects.values_list('user_id', flat=True))
    duplicates = brand_user_ids & bp_user_ids
    
    print(f"\nDuplicate users (in both Brand and BrandProfile): {len(duplicates)}")
    
    if duplicates:
        print("  These will be merged during migration")
        for user_id in list(duplicates)[:3]:
            brand = Brand.objects.get(user_id=user_id)
            bp = BrandProfile.objects.get(user_id=user_id)
            print(f"    - User {user_id}: Brand('{brand.brand_name}') vs BrandProfile('{bp.brand_name}')")
    
except Exception as e:
    print(f"  ⚠️  BrandProfile table doesn't exist: {e}")

# Analysis 4: Data quality issues
print("\n📊 ANALYSIS 4: Data Quality Issues")

missing_nib = Brand.objects.filter(Q(nib_or_ktp__isnull=True) | Q(nib_or_ktp='')).count()
print(f"Brands missing nib_or_ktp: {missing_nib}")

zero_rating = Brand.objects.filter(rating=0.0).count()
print(f"Brands with rating=0: {zero_rating}")

# Analysis 5: Related data integrity
print("\n📊 ANALYSIS 5: Related Data Integrity")

orphan_products = Product.objects.filter(brand_id__isnull=True).count()
print(f"Orphaned products (no brand): {orphan_products}")

orphan_orders = Order.objects.filter(brand_id__isnull=True).count()
print(f"Orphaned orders (no brand): {orphan_orders}")

# Export data
print("\n📊 DATA EXPORT:")
data = {
    'total_brands': Brand.objects.count(),
    'total_products': Product.objects.count(),
    'total_orders': Order.objects.count(),
    'brand_status_distribution': dict(
        (s['status'], s['count']) for s in Brand.objects.values('status').annotate(count=Count('status'))
    ),
    'missing_fields': {
        'nib_or_ktp': missing_nib,
        'rating_zero': zero_rating,
    },
    'orphaned_records': {
        'products': orphan_products,
        'orders': orphan_orders,
    }
}

# Save to file
with open('brand_analysis.json', 'w') as f:
    json.dump(data, f, indent=2)
    print("Data exported to: brand_analysis.json")

print("\n" + "=" * 60)
```

---

## 🔍 SCRIPT 6: Rollback Procedure

**File**: `rollback_brand_consolidation.py`

**Location**: Project root

**Usage** (if migration fails):
```bash
python rollback_brand_consolidation.py
```

```python
#!/usr/bin/env python
"""
Rollback Brand consolidation to previous state
Use only if migration fails and you need to restore
"""

import os
import shutil
from datetime import datetime

print("=" * 70)
print("BRAND CONSOLIDATION ROLLBACK PROCEDURE")
print("=" * 70)

print("\n⚠️  WARNING: This will restore database from backup!")
print("Continuing in 10 seconds... (Ctrl+C to cancel)")

import time
try:
    for i in range(10, 0, -1):
        print(f"\r  {i} seconds...", end='', flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    print("\n✋ Rollback cancelled")
    exit()

print("\n")

try:
    # Find latest backup
    backups = sorted([f for f in os.listdir('.') if f.startswith('db_backup_')])
    
    if not backups:
        print("❌ No backup files found!")
        print("   Expected format: db_backup_YYYYMMDD_HHMMSS.sqlite3")
        exit(1)
    
    latest_backup = backups[-1]
    print(f"[1/3] Found latest backup: {latest_backup}")
    
    # Backup current (failed) database
    failed_db = f"db_migration_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
    shutil.copy('db.sqlite3', failed_db)
    print(f"[2/3] Saved failed database to: {failed_db}")
    
    # Restore backup
    shutil.copy(latest_backup, 'db.sqlite3')
    print(f"[3/3] Restored database from: {latest_backup}")
    
    print("\n✅ ROLLBACK COMPLETED")
    print("\nNext steps:")
    print("  1. Review failed migration logs")
    print("  2. Fix issues in code/migration files")
    print("  3. Try migration again")
    print("\nBackup files:")
    print(f"  Original: {latest_backup}")
    print(f"  Failed: {failed_db}")
    
except Exception as e:
    print(f"\n❌ ROLLBACK FAILED: {e}")
    import traceback
    traceback.print_exc()
```

---

## 📋 CHECKLISTS

### Pre-Migration Checklist

```
□ Code changes completed (models, views, admin)
□ Migration files created (0002, 0003, and deletion)
□ Data migration script reviewed and tested
□ Database backup created
□ Server stopped
□ No active users connected
□ Pre-migration verification ran successfully
□ Team informed of maintenance window
```

### Post-Migration Checklist

```
□ All migrations applied successfully
□ Database check passed (python manage.py check)
□ Post-migration verification ran successfully
□ Admin interface shows new fields
□ Add product workflow tested
□ Checkout workflow tested
□ Product detail page works
□ Order history page works
□ No errors in Django logs
□ Backup retained (in case of rollback)
□ Performance acceptable (< 500ms page load)
□ Team notified of completion
```

---

**Status**: ✅ ALL SCRIPTS READY
**Date**: 19 Juni 2026
**Usage**: Copy-paste into appropriate locations and run

