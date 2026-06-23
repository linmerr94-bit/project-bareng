#!/usr/bin/env python
"""
Script untuk populate test data ke database
Membuat brands, categories, dan products dengan dual pricing B2B/B2C
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
sys.path.insert(0, 'D:\\PROJEK UAS E-COMMERCE')
django.setup()

from django.contrib.auth.models import User
from master_brands.models import BrandProfile
from master_products.models import Category, Product


def create_test_data():
    """Membuat data test untuk demstrasi B2B2C VOLTA"""
    
    print("=" * 60)
    print("POPULATE TEST DATA - VOLTA E-Commerce Platform")
    print("=" * 60)
    
    # 1. Create Test Categories
    print("\n[1] Creating Categories...")
    categories_data = [
        {
            'name': 'Smartphone',
            'description': 'Ponsel pintar dan fitur canggih terkini'
        },
        {
            'name': 'Laptop',
            'description': 'Laptop performa tinggi untuk bisnis dan gaming'
        },
        {
            'name': 'Audio',
            'description': 'Speaker, headphone, dan sistem audio premium'
        },
        {
            'name': 'Smart Home',
            'description': 'Perangkat rumah pintar dan IoT'
        },
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description'], 'is_active': True}
        )
        categories[cat_data['name']] = category
        status = "✓ Created" if created else "✓ Already exists"
        print(f"  {status}: {category.name}")
    
    # 2. Create Test Brands (Sellers)
    print("\n[2] Creating Brands/Sellers...")
    brands_data = [
        {
            'username': 'brandsamsung',
            'email': 'samsung@volta.com',
            'brand_name': 'Samsung Indonesia',
            'nib_or_ktp': '12.345.678.901.234'
        },
        {
            'username': 'brandapple',
            'email': 'apple@volta.com',
            'brand_name': 'Apple Authorized',
            'nib_or_ktp': '98.765.432.109.876'
        },
        {
            'username': 'brandasus',
            'email': 'asus@volta.com',
            'brand_name': 'ASUS Indonesia',
            'nib_or_ktp': '11.222.333.444.555'
        },
    ]
    
    brands = {}
    for brand_data in brands_data:
        # Create user
        user, user_created = User.objects.get_or_create(
            username=brand_data['username'],
            defaults={
                'email': brand_data['email'],
                'first_name': brand_data['brand_name'].split()[0]
            }
        )
        
        # Create brand profile
        brand_profile, brand_created = BrandProfile.objects.get_or_create(
            user=user,
            defaults={
                'brand_name': brand_data['brand_name'],
                'nib_or_ktp': brand_data['nib_or_ktp'],
                'status': 'APPROVED',  # Set to APPROVED for testing
                'rating': 4.5
            }
        )
        brands[brand_data['brand_name']] = brand_profile
        status = "✓ Created" if brand_created else "✓ Already exists"
        print(f"  {status}: {brand_profile.brand_name} ({brand_profile.status})")
    
    # 3. Create Test Products with B2B/B2C Pricing
    print("\n[3] Creating Products with B2B/B2C Pricing...")
    products_data = [
        # Smartphones
        {
            'brand_name': 'Samsung Indonesia',
            'category_name': 'Smartphone',
            'name': 'Samsung Galaxy S24 Ultra',
            'sku': 'SGS24ULTRA001',
            'description': 'Flagship smartphone dengan processor Snapdragon 8 Gen 3',
            'price_b2c': Decimal('20000000'),  # 20 juta (retail)
            'price_b2b': Decimal('15000000'),  # 15 juta (wholesale)
            'moq_b2b': 5,
            'stock': 50,
            'rating': 4.8
        },
        {
            'brand_name': 'Apple Authorized',
            'category_name': 'Smartphone',
            'name': 'iPhone 15 Pro Max',
            'sku': 'IPH15PROMAX001',
            'description': 'Premium iPhone dengan chip A17 Pro',
            'price_b2c': Decimal('22000000'),
            'price_b2b': Decimal('18000000'),
            'moq_b2b': 3,
            'stock': 30,
            'rating': 4.9
        },
        # Laptops
        {
            'brand_name': 'ASUS Indonesia',
            'category_name': 'Laptop',
            'name': 'ASUS ROG Zephyrus G16',
            'sku': 'ASUS-ROG-G16-001',
            'description': 'Gaming laptop dengan RTX 4090 dan Intel Core i9',
            'price_b2c': Decimal('35000000'),
            'price_b2b': Decimal('28000000'),
            'moq_b2b': 2,
            'stock': 25,
            'rating': 4.7
        },
        {
            'brand_name': 'Apple Authorized',
            'category_name': 'Laptop',
            'name': 'MacBook Pro 16" M3 Max',
            'sku': 'MBP16-M3MAX-001',
            'description': 'Professional laptop dengan M3 Max chip dan 48GB RAM',
            'price_b2c': Decimal('40000000'),
            'price_b2b': Decimal('32000000'),
            'moq_b2b': 1,
            'stock': 15,
            'rating': 5.0
        },
        # Audio
        {
            'brand_name': 'Samsung Indonesia',
            'category_name': 'Audio',
            'name': 'Samsung Galaxy Buds2 Pro',
            'sku': 'SGW-BUDS2PRO-001',
            'description': 'True wireless earbuds dengan ANC aktif',
            'price_b2c': Decimal('3500000'),
            'price_b2b': Decimal('2500000'),
            'moq_b2b': 10,
            'stock': 200,
            'rating': 4.5
        },
        # Smart Home
        {
            'brand_name': 'ASUS Indonesia',
            'category_name': 'Smart Home',
            'name': 'Smart WiFi Router ASUS AX6000',
            'sku': 'ASUS-WIFI-AX6000-001',
            'description': 'Router WiFi 6 dengan jangkauan hingga 200m2',
            'price_b2c': Decimal('2500000'),
            'price_b2b': Decimal('1800000'),
            'moq_b2b': 5,
            'stock': 100,
            'rating': 4.6
        },
    ]
    
    for prod_data in products_data:
        brand = brands.get(prod_data['brand_name'])
        category = categories.get(prod_data['category_name'])
        
        if not brand or not category:
            print(f"  ✗ Skipped: {prod_data['name']} (brand/category not found)")
            continue
        
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'brand': brand,
                'category': category,
                'name': prod_data['name'],
                'description': prod_data['description'],
                'price_b2c': prod_data['price_b2c'],
                'price_b2b': prod_data['price_b2b'],
                'moq_b2b': prod_data['moq_b2b'],
                'stock': prod_data['stock'],
                'rating': prod_data['rating'],
                'is_active': True,
            }
        )
        
        status = "✓ Created" if created else "✓ Already exists"
        discount = int(((prod_data['price_b2c'] - prod_data['price_b2b']) / prod_data['price_b2c']) * 100)
        print(f"  {status}: {product.name}")
        print(f"           B2C: Rp {prod_data['price_b2c']:,} | B2B: Rp {prod_data['price_b2b']:,} ({discount}% off)")
    
    print("\n" + "=" * 60)
    print("✓ Test Data Population Complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Categories: {Category.objects.count()}")
    print(f"  - Brands: {BrandProfile.objects.count()}")
    print(f"  - Products: {Product.objects.count()}")
    print(f"  - Products Active: {Product.objects.filter(is_active=True).count()}")
    print(f"\nURL: http://127.0.0.1:8000/")
    print("=" * 60)


if __name__ == '__main__':
    create_test_data()
