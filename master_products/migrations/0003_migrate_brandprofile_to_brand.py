from django.db import migrations

def migrate_brandprofile_to_brand(apps, schema_editor):
    """
    Migrate data dari BrandProfile (master_brands) ke Brand (master_products)
    
    Process:
    1. For each BrandProfile record
    2. If Brand exists for same user: UPDATE (merge)
    3. If Brand doesn't exist: CREATE from BrandProfile
    4. Normalize status values (UPPERCASE → lowercase)
    5. Map nib_or_ktp and rating fields
    """
    Brand = apps.get_model('master_products', 'Brand')
    
    try:
        # Import BrandProfile from apps (will work even after table is deleted in reverse)
        BrandProfile = apps.get_model('master_brands', 'BrandProfile')
        
        migrated_count = 0
        updated_count = 0
        error_count = 0
        
        for bp in BrandProfile.objects.all():
            try:
                # Check if Brand sudah ada untuk user ini
                try:
                    brand = Brand.objects.get(user_id=bp.user)
                    
                    # Update existing Brand dengan data dari BrandProfile
                    brand.nib_or_ktp = bp.nib_or_ktp
                    brand.rating = bp.rating
                    
                    # Map status dari BrandProfile ke Brand (normalize case)
                    if bp.status == 'PENDING':
                        brand.status = 'pending'
                    elif bp.status == 'APPROVED':
                        brand.status = 'approved'
                    elif bp.status == 'SUSPENDED':
                        brand.status = 'suspended'
                    else:
                        brand.status = bp.status.lower()
                    
                    brand.save()
                    updated_count += 1
                    print(f"✓ Updated Brand: {brand.brand_name}")
                    
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
                    else:
                        brand.status = bp.status.lower()
                    
                    brand.save()
                    migrated_count += 1
                    print(f"✓ Migrated Brand: {brand.brand_name}")
            
            except Exception as e:
                error_count += 1
                print(f"✗ Error processing BrandProfile {bp.brand_name}: {e}")
        
        print(f"\n{'='*50}")
        print(f"MIGRATION SUMMARY")
        print(f"{'='*50}")
        print(f"New Brands created:     {migrated_count}")
        print(f"Existing Brands updated: {updated_count}")
        print(f"Errors:                  {error_count}")
        print(f"Total processed:        {BrandProfile.objects.count()}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()


def reverse_migrate(apps, schema_editor):
    """
    Rollback: Clear nib_or_ktp dan rating dari Brand
    (Jangan delete Brand records karena sudah digunakan oleh Product & Order)
    """
    Brand = apps.get_model('master_products', 'Brand')
    Brand.objects.all().update(nib_or_ktp=None, rating=0.0)
    print("✓ Rollback complete: nib_or_ktp dan rating cleared from Brand")


class Migration(migrations.Migration):

    dependencies = [
        ('master_products', '0002_add_nib_rating_to_brand'),
    ]

    operations = [
        migrations.RunPython(migrate_brandprofile_to_brand, reverse_migrate),
    ]
