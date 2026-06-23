# Generated migration for deleting BrandProfile model
# BrandProfile has been consolidated into Brand model (master_products)
# 
# ⚠️ IMPORTANT: This migration depends on 0003_migrate_brandprofile_to_brand
# to ensure data is migrated BEFORE the table is deleted

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_brands', '0001_initial'),
        ('master_products', '0003_migrate_brandprofile_to_brand'),  # ✓ Data migration must complete first
    ]

    operations = [
        migrations.DeleteModel(
            name='BrandProfile',
        ),
    ]
