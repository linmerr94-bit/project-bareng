#!/usr/bin/env python
"""
Script sederhana untuk mengisi database dengan data sampel
Jalankan dengan: python seed_database.py
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from users.models import User
from master_products.models import Category, Brand, Product


def create_sample_data():
    """Membuat data sampel untuk testing"""
    
    print("\n" + "=" * 70)
    print("🌟 POPULATE SAMPLE DATA - VOLTA E-Commerce Platform")
    print("=" * 70 + "\n")

    # =====================================================================
    # 1. CREATE CATEGORIES
    # =====================================================================
    print("[1] Creating Categories...")
    
    categories_data = [
        {
            'category_name': 'Elektronik',
            'description': 'Produk elektronik dan gadget terkini seperti smartphone, laptop, dan aksesoris'
        },
        {
            'category_name': 'Pakaian',
            'description': 'Koleksi pakaian fashion modern untuk pria, wanita, dan anak-anak'
        },
        {
            'category_name': 'Aksesoris',
            'description': 'Aksesori fashion dan gadget seperti tas, dompet, dan charger'
        },
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            category_name=cat_data['category_name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['category_name']] = category
        status = "✓ Dibuat" if created else "✓ Sudah ada"
        print(f"  {status}: {category.category_name}")

    # =====================================================================
    # 2. CREATE BRAND USERS & BRANDS
    # =====================================================================
    print("\n[2] Creating Brands/Vendors...")
    
    brands_data = [
        {
            'username': 'samsung_store',
            'email': 'samsung@volta.com',
            'brand_name': 'Samsung Official Store',
            'first_name': 'Samsung'
        },
        {
            'username': 'apple_authorized',
            'email': 'apple@volta.com',
            'brand_name': 'Apple Authorized Partner',
            'first_name': 'Apple'
        },
        {
            'username': 'asus_official',
            'email': 'asus@volta.com',
            'brand_name': 'ASUS Indonesia',
            'first_name': 'ASUS'
        },
    ]
    
    brands = {}
    for brand_data in brands_data:
        # Buat user untuk brand
        user, user_created = User.objects.get_or_create(
            username=brand_data['username'],
            defaults={
                'email': brand_data['email'],
                'first_name': brand_data['first_name'],
                'role': 'brand',  # Set role sebagai brand
                'is_active': True
            }
        )
        
        # Buat brand profile
        brand, brand_created = Brand.objects.get_or_create(
            user_id=user,
            defaults={
                'brand_name': brand_data['brand_name'],
                'status': 'approved',  # Langsung approved untuk testing
                'description': f'Toko resmi {brand_data["brand_name"]} dengan produk berkualitas'
            }
        )
        
        brands[brand_data['brand_name']] = brand
        status = "✓ Dibuat" if brand_created else "✓ Sudah ada"
        print(f"  {status}: {brand.brand_name} (User: {user.username})")

    # =====================================================================
    # 3. CREATE PRODUCTS
    # =====================================================================
    print("\n[3] Creating Products...")
    
    products_data = [
        {
            'product_name': 'Samsung Galaxy S24 Ultra',
            'description': 'Smartphone flagship dengan AI camera dan display 6.8 inch AMOLED. Performa maksimal dengan Snapdragon Gen 3 Leading Version.',
            'category': 'Elektronik',
            'brand': 'Samsung Official Store',
            'price': Decimal('15999999.00'),
            'stock': 25
        },
        {
            'product_name': 'Apple iPhone 15 Pro Max',
            'description': 'Smartphone premium dengan chip A17 Pro, camera 48MP, dan design titanium. Performa lightning-fast untuk semua kebutuhan.',
            'category': 'Elektronik',
            'brand': 'Apple Authorized Partner',
            'price': Decimal('19999999.00'),
            'stock': 18
        },
        {
            'product_name': 'ASUS VivoBook 15 OLED',
            'description': 'Laptop 15.6 inch dengan layar OLED, Intel Core i7, RAM 16GB, SSD 512GB. Sempurna untuk desain grafis dan editing video.',
            'category': 'Elektronik',
            'brand': 'ASUS Indonesia',
            'price': Decimal('12999999.00'),
            'stock': 12
        },
        {
            'product_name': 'Samsung Galaxy Buds3 Pro',
            'description': 'Earbuds wireless dengan ANC (Active Noise Cancellation), sound quality premium, dan battery life hingga 26 jam.',
            'category': 'Aksesoris',
            'brand': 'Samsung Official Store',
            'price': Decimal('2299999.00'),
            'stock': 50
        },
        {
            'product_name': 'ASUS Gaming Laptop ROG',
            'description': 'Laptop gaming dengan RTX 4070, Intel Core i9, 32GB RAM. Refresh rate 240Hz untuk performa gaming maksimal.',
            'category': 'Elektronik',
            'brand': 'ASUS Indonesia',
            'price': Decimal('24999999.00'),
            'stock': 8
        },
    ]
    
    for prod_data in products_data:
        # Generate slug otomatis dari product_name
        slug = prod_data['product_name'].lower().replace(' ', '-')
        
        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'product_name': prod_data['product_name'],
                'description': prod_data['description'],
                'category_id': categories[prod_data['category']],
                'brand_id': brands[prod_data['brand']],
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'is_active': True
            }
        )
        
        status = "✓ Dibuat" if created else "✓ Sudah ada"
        price_formatted = f"Rp {prod_data['price']:,.0f}".replace(',', '.')
        print(f"  {status}: {product.product_name}")
        print(f"           Harga: {price_formatted} | Stok: {prod_data['stock']} unit")

    # =====================================================================
    # SUMMARY
    # =====================================================================
    print("\n" + "=" * 70)
    print("✓ DATA SAMPEL BERHASIL DIISI KE DATABASE!")
    print("=" * 70)
    
    print("\n📊 Summary:")
    print(f'   • Categories: {len(categories_data)} kategori')
    print(f'   • Brands: {len(brands_data)} brand/vendor')
    print(f'   • Products: {len(products_data)} produk')
    
    print("\n🌐 URL untuk Testing:")
    print('   • Homepage: http://localhost:8000/master_products/product_list/')
    print('   • Admin: http://localhost:8000/admin/')
    print('   • Username: admin')
    print('   • Password: admin123')
    
    print("\n✨ Selesai! Database siap untuk testing.\n")


if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
