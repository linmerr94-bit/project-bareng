"""
Management command untuk seed data sampel ke database.
Membuat 3 kategori, 3 brand, dan 5 produk sampel.

Penggunaan:
    python manage.py seed_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from master_products.models import Category, Brand, Product
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database dengan data sampel (kategori, brand, produk)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Mulai Seed Data Sampel ===\n'))

        # ===== 1. CREATE CATEGORIES =====
        self.stdout.write('📦 Membuat kategori...')
        categories_data = [
            {
                'category_name': 'Elektronik',
                'description': 'Produk elektronik seperti gadget, laptop, dan aksesoris elektronik'
            },
            {
                'category_name': 'Pakaian',
                'description': 'Pakaian dan fashion items untuk pria dan wanita'
            },
            {
                'category_name': 'Aksesoris',
                'description': 'Berbagai aksesoris fashion seperti tas, dompet, dan perhiasan'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                category_name=cat_data['category_name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['category_name']] = cat
            status = '✓ Dibuat' if created else '⚠ Sudah ada'
            self.stdout.write(f"  {status}: {cat.category_name}")

        # ===== 2. CREATE USERS (untuk brand) =====
        self.stdout.write('\n👥 Membuat user/vendor...')
        users_data = [
            {'username': 'vendor_elektronik', 'email': 'vendor1@example.com', 'password': 'VendorPassword123!'},
            {'username': 'vendor_fashion', 'email': 'vendor2@example.com', 'password': 'VendorPassword123!'},
            {'username': 'vendor_aksesoris', 'email': 'vendor3@example.com', 'password': 'VendorPassword123!'},
        ]

        users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"  ✓ Dibuat: {user.username}")
            else:
                self.stdout.write(f"  ⚠ Sudah ada: {user.username}")
            users[user_data['username']] = user

        # ===== 3. CREATE BRANDS =====
        self.stdout.write('\n🏪 Membuat brand...')
        brands_data = [
            {
                'username': 'vendor_elektronik',
                'brand_name': 'TechHub Indonesia',
                'description': 'Penyedia gadget dan elektronik terpercaya'
            },
            {
                'username': 'vendor_fashion',
                'brand_name': 'StylePro Boutique',
                'description': 'Butik fashion terkini dengan koleksi eksklusif'
            },
            {
                'username': 'vendor_aksesoris',
                'brand_name': 'Aksesori Prime',
                'description': 'Aksesoris berkualitas dengan desain modern'
            }
        ]

        brands = {}
        for brand_data in brands_data:
            user = users[brand_data['username']]
            brand, created = Brand.objects.get_or_create(
                user_id=user,
                defaults={
                    'brand_name': brand_data['brand_name'],
                    'description': brand_data['description'],
                    'status': 'approved',  # Set langsung ke APPROVED
                    'approved_at': datetime.now()
                }
            )
            if created:
                self.stdout.write(f"  ✓ Dibuat: {brand.brand_name} - Status: APPROVED")
            else:
                # Update status jika belum approved
                if brand.status != 'approved':
                    brand.status = 'approved'
                    brand.approved_at = datetime.now()
                    brand.save()
                    self.stdout.write(f"  ⚠ Sudah ada & di-update ke APPROVED: {brand.brand_name}")
                else:
                    self.stdout.write(f"  ⚠ Sudah ada: {brand.brand_name}")
            brands[brand_data['brand_name']] = brand

        # ===== 4. CREATE PRODUCTS =====
        self.stdout.write('\n📱 Membuat produk sampel...')
        products_data = [
            {
                'brand': 'TechHub Indonesia',
                'category': 'Elektronik',
                'product_name': 'Laptop Gaming Pro 15"',
                'description': 'Laptop gaming dengan prosesor terbaru, GPU RTX 4060, RAM 16GB',
                'price': 12999999.99,
                'stock': 15
            },
            {
                'brand': 'TechHub Indonesia',
                'category': 'Elektronik',
                'product_name': 'Smartphone XZB 13 Pro',
                'description': 'Smartphone flagship dengan kamera 200MP dan layar AMOLED 6.8"',
                'price': 8999999.99,
                'stock': 25
            },
            {
                'brand': 'StylePro Boutique',
                'category': 'Pakaian',
                'product_name': 'Kemeja Katun Premium Pria',
                'description': 'Kemeja pria dari bahan katun 100% premium dengan jahitan rapi',
                'price': 349999.99,
                'stock': 50
            },
            {
                'brand': 'StylePro Boutique',
                'category': 'Pakaian',
                'product_name': 'Dress Kasual Wanita',
                'description': 'Dress wanita casual modern dengan desain minimalis dan nyaman',
                'price': 449999.99,
                'stock': 40
            },
            {
                'brand': 'Aksesori Prime',
                'category': 'Aksesoris',
                'product_name': 'Tas Tangan Kulit Asli',
                'description': 'Tas tangan dari kulit asli berkualitas tinggi dengan desain elegan',
                'price': 1299999.99,
                'stock': 20
            },
            {
                'brand': 'Aksesori Prime',
                'category': 'Aksesoris',
                'product_name': 'Dompet Kulit Bifold',
                'description': 'Dompet pria dari kulit asli dengan banyak kompartemen',
                'price': 549999.99,
                'stock': 35
            },
            {
                'brand': 'TechHub Indonesia',
                'category': 'Elektronik',
                'product_name': 'Headphone Wireless Noise Cancelling',
                'description': 'Headphone wireless dengan teknologi noise cancelling aktif',
                'price': 2499999.99,
                'stock': 18
            }
        ]

        for prod_data in products_data:
            # Generate slug otomatis
            slug = slugify(prod_data['product_name'])

            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'brand_id': brands[prod_data['brand']],
                    'category_id': categories[prod_data['category']],
                    'product_name': prod_data['product_name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'is_active': True  # Semua produk aktif
                }
            )

            if created:
                self.stdout.write(
                    f"  ✓ Dibuat: {prod_data['product_name']} | Rp{prod_data['price']:,.0f} | "
                    f"Stok: {prod_data['stock']}"
                )
            else:
                self.stdout.write(f"  ⚠ Sudah ada: {prod_data['product_name']}")

        # ===== SUMMARY =====
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✓ Seed Data Berhasil Dikomplekkan!'))
        self.stdout.write(self.style.SUCCESS('='*50))

        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Kategori: {Category.objects.count()}')
        self.stdout.write(f'  • Brand (Approved): {Brand.objects.filter(status="approved").count()}')
        self.stdout.write(f'  • Produk (Aktif): {Product.objects.filter(is_active=True).count()}')
        self.stdout.write(f'\n✨ Halaman depan Anda sudah siap dengan data sampel!\n')
