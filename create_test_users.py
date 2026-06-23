#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

from users.models import User
from master_products.models import Brand

# Create or reset admin test user
user, created = User.objects.update_or_create(
    username='admin_volta',
    defaults={
        'email': 'admin@volta.test',
        'first_name': 'Admin',
        'last_name': 'VOLTA',
        'role': 'admin',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True
    }
)
user.set_password('admin123')
user.save()
print(f"Admin user created/updated: {user.username}")

# Create seller test user
seller, _ = User.objects.update_or_create(
    username='seller_volta',
    defaults={
        'email': 'seller@volta.test',
        'first_name': 'Seller',
        'last_name': 'Test',
        'role': 'brand',
        'is_superuser': False,
        'is_staff': False,
        'is_active': True
    }
)
seller.set_password('seller123')
seller.save()
print(f"Seller user created/updated: {seller.username}")

# Create brand for seller
brand, _ = Brand.objects.update_or_create(
    user_id=seller,
    defaults={
        'brand_name': 'VOLTA Test Shop',
        'description': 'Toko test untuk fitur seller dashboard',
        'status': 'approved'
    }
)
print(f"Brand created/updated: {brand.brand_name} for {seller.username}")
