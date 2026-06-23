"""
Management Command: Seed Data Toko Elektronik Lokal Purwokerto

Membuat database VOLTA dengan konteks "Toko Elektronik Lokal Purwokerto":
- 3 Brand: Sinar Baru Elektronik, Banyumas Computer, Toko Python Elektronik
- 4 Kategori: Elektronik Rumah Tangga, Komputer & Laptop, Komponen & Aksesoris, Handphone
- 15+ Produk sampel dengan harga relevan
- Status: 2 approved, 1 pending (untuk test Admin Platform approval)

Penggunaan:
    python manage.py seed_purwokerto_electronics

Fitur:
- ✓ Menghapus semua data lama (kategori, brand, produk yang tidak relevan)
- ✓ Membuat kategori elektronik lokal
- ✓ Membuat 3 brand dengan konteks Purwokerto
- ✓ Menggunakan URL placeholder Unsplash untuk gambar
- ✓ Membuat produk sampel untuk setiap brand
- ✓ Set 2 brand ke 'approved', 1 ke 'pending'
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from master_products.models import Category, Brand, Product
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database dengan data Toko Elektronik Lokal Purwokerto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Hapus semua data lama sebelum seed (default: ya)',
        )

    def handle(self, *args, **options):
        clean_data = options.get('clean', True)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🎯 SEED DATA: Toko Elektronik Lokal Purwokerto'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # ===== 0. CLEAN OLD DATA =====
        if clean_data:
            self._clean_old_data()

        # ===== 1. CREATE CATEGORIES =====
        self._create_categories()

        # ===== 2. CREATE USERS (untuk brand) =====
        users = self._create_users()

        # ===== 3. CREATE BRANDS =====
        brands = self._create_brands(users)

        # ===== 4. CREATE PRODUCTS =====
        self._create_products(brands)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ Seed Data Selesai!'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

    def _clean_old_data(self):
        """Hapus semua data lama"""
        self.stdout.write(self.style.WARNING('\n🗑️  MEMBERSIHKAN DATA LAMA...\n'))

        # Hapus semua products
        product_count = Product.objects.all().count()
        if product_count > 0:
            Product.objects.all().delete()
            self.stdout.write(f"  ✓ Dihapus: {product_count} produk lama")

        # Hapus semua brands
        brand_count = Brand.objects.all().count()
        if brand_count > 0:
            Brand.objects.all().delete()
            self.stdout.write(f"  ✓ Dihapus: {brand_count} brand lama")

        # Hapus kategori yang tidak relevan (pakaian, aksesoris, dll)
        irrelevant_categories = [
            'Pakaian', 'Fashion', 'Aksesoris', 'Grosir', 'Fashion Item',
            'Clothing', 'Accessories', 'Apparel'
        ]
        for cat_name in irrelevant_categories:
            deleted_count, _ = Category.objects.filter(
                category_name__iexact=cat_name
            ).delete()
            if deleted_count > 0:
                self.stdout.write(f"  ✓ Dihapus: Kategori '{cat_name}'")

        # Hapus user/vendor yang tidak digunakan
        irrelevant_users = [
            'vendor_elektronik', 'vendor_fashion', 'vendor_aksesoris',
            'vendor1', 'vendor2', 'vendor3'
        ]
        for username in irrelevant_users:
            deleted_count, _ = User.objects.filter(
                username__iexact=username,
                role='brand'
            ).delete()
            if deleted_count > 0:
                self.stdout.write(f"  ✓ Dihapus: User vendor '{username}'")

    def _create_categories(self):
        """Buat kategori elektronik"""
        self.stdout.write(self.style.SUCCESS('\n📦 MEMBUAT KATEGORI...\n'))

        categories_data = [
            {
                'category_name': 'Elektronik Rumah Tangga',
                'description': 'TV, Kulkas, AC, Mesin Cuci, dan peralatan rumah tangga lainnya'
            },
            {
                'category_name': 'Komputer & Laptop',
                'description': 'Laptop, Desktop, PC Gaming, dan aksesoris komputer'
            },
            {
                'category_name': 'Komponen & Aksesoris Elektronik',
                'description': 'Suku cadang elektronik, robotika, dan aksesoris IT'
            },
            {
                'category_name': 'Handphone',
                'description': 'Smartphone, tablet, dan aksesoris mobile'
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

        return categories

    def _create_users(self):
        """Buat user/vendor untuk 3 brand"""
        self.stdout.write(self.style.SUCCESS('\n👥 MEMBUAT USER/VENDOR...\n'))

        users_data = [
            {
                'username': 'sinar_baru_purwokerto',
                'email': 'info@sinarbaru.local',
                'password': 'SinarBaru123!Purwokerto'
            },
            {
                'username': 'banyumas_computer',
                'email': 'admin@banyumascomputer.local',
                'password': 'BanyumasComputer123!'
            },
            {
                'username': 'toko_python_elektronik',
                'email': 'info@tokopython.local',
                'password': 'TokoPython123!Elektronik'
            }
        ]

        users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'full_name': user_data['username'].replace('_', ' ').title(),
                    'role': 'brand',
                    'is_staff': False
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"  ✓ Dibuat: {user.username}")
            else:
                self.stdout.write(f"  ⚠ Sudah ada: {user.username}")

            users[user_data['username']] = user

        return users

    def _create_brands(self, users):
        """Buat 3 brand dengan konteks Purwokerto"""
        self.stdout.write(self.style.SUCCESS('\n🏪 MEMBUAT BRAND...\n'))

        brands_data = [
            {
                'username': 'sinar_baru_purwokerto',
                'brand_name': 'Sinar Baru Elektronik Purwokerto',
                'description': 'Penyedia elektronik rumah tangga terlengkap di Purwokerto. Kami menawarkan berbagai produk elektronik berkualitas dengan harga terjangkau.',
                'status': 'approved',
                'nib_or_ktp': '123456789101112',
                'logo_url': 'https://images.unsplash.com/photo-1558317374-067fb5f30001'  # Home Appliances
            },
            {
                'username': 'banyumas_computer',
                'brand_name': 'Banyumas Computer',
                'description': 'Pusat laptop dan aksesoris IT terpercaya di Purwokerto. Spesialis penjualan komputer, laptop gaming, dan spare parts original.',
                'status': 'approved',
                'nib_or_ktp': '987654321101112',
                'logo_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed'  # Laptop/PC
            },
            {
                'username': 'toko_python_elektronik',
                'brand_name': 'Toko Python Elektronik',
                'description': 'Toko komponen robotika dan suku cadang elektronik terlengkap di Purwokerto Utara. Melayani kebutuhan komponen untuk hobi dan industri.',
                'status': 'pending',
                'nib_or_ktp': '555666777101112',
                'logo_url': 'https://images.unsplash.com/photo-1517059224940-d4af9eec41b7'  # Komponen Elektronik
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
                    'status': brand_data['status'],
                    'nib_or_ktp': brand_data['nib_or_ktp'],
                    'rating': Decimal('4.5'),
                    'logo': brand_data['logo_url'],
                    'approved_at': timezone.now() if brand_data['status'] == 'approved' else None
                }
            )

            if created:
                status_emoji = '✅' if brand_data['status'] == 'approved' else '⏳'
                self.stdout.write(
                    f"  {status_emoji} Dibuat: {brand.brand_name} "
                    f"({brand_data['status'].upper()})"
                )
            else:
                status_emoji = '✅' if brand_data['status'] == 'approved' else '⏳'
                self.stdout.write(
                    f"  ⚠ Sudah ada: {brand.brand_name} "
                    f"({brand_data['status'].upper()})"
                )

            brands[brand_data['username']] = brand

        return brands

    def _create_products(self, brands):
        """Buat produk untuk masing-masing brand"""
        self.stdout.write(self.style.SUCCESS('\n📱 MEMBUAT PRODUK SAMPEL...\n'))

        # Produk untuk Sinar Baru Elektronik Purwokerto
        sinar_baru_products = [
            {
                'product_name': 'TV LED 55 Inch 4K Smart',
                'category': 'Elektronik Rumah Tangga',
                'description': 'Smart TV LED 55 inch dengan resolusi 4K, teknologi HDR, dan built-in streaming apps. Cocok untuk home entertainment premium.',
                'price': Decimal('4999999.99'),
                'stock': 12,
                'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211'
            },
            {
                'product_name': 'Kulkas 2 Pintu Inverter 450L',
                'category': 'Elektronik Rumah Tangga',
                'description': 'Kulkas side-by-side dengan kapasitas 450 liter, teknologi inverter hemat energi, dan ice maker otomatis.',
                'price': Decimal('6799999.99'),
                'stock': 8,
                'image_url': 'https://images.unsplash.com/photo-1584622181563-430f63602d4b'
            },
            {
                'product_name': 'AC Split 2 PK Inverter',
                'category': 'Elektronik Rumah Tangga',
                'description': 'Air Conditioner split 2 PK dengan teknologi inverter, hemat listrik, dan dilengkapi mode sleep yang nyaman.',
                'price': Decimal('2999999.99'),
                'stock': 15,
                'image_url': 'https://images.unsplash.com/photo-1529148482759-b649eaa42a71'
            },
            {
                'product_name': 'Mesin Cuci 8 Kg Full Automatic',
                'category': 'Elektronik Rumah Tangga',
                'description': 'Mesin cuci otomatis 8 kg dengan 8 program pencucian, tabung stainless steel, dan hemat air & listrik.',
                'price': Decimal('2499999.99'),
                'stock': 10,
                'image_url': 'https://images.unsplash.com/photo-1517701550927-30cf4ba53dba'
            },
            {
                'product_name': 'Dispenser Air Panas Dingin Premium',
                'category': 'Elektronik Rumah Tangga',
                'description': 'Dispenser air dengan teknologi panas dingin, keamanan child lock, dan efisiensi energi tinggi.',
                'price': Decimal('1299999.99'),
                'stock': 20,
                'image_url': 'https://images.unsplash.com/photo-1585604088235-bf461a977ffe'
            }
        ]

        # Produk untuk Banyumas Computer
        banyumas_computer_products = [
            {
                'product_name': 'Laptop Gaming ASUS ROG 15.6"',
                'category': 'Komputer & Laptop',
                'description': 'Laptop gaming dengan Intel i7, RTX 4060, RAM 16GB, SSD 512GB, refresh rate 144Hz, sempurna untuk gaming dan desain.',
                'price': Decimal('13999999.99'),
                'stock': 7,
                'image_url': 'https://images.unsplash.com/photo-1503387762519-52582e360e90'
            },
            {
                'product_name': 'Laptop Kerja Dell Inspiron 15"',
                'category': 'Komputer & Laptop',
                'description': 'Laptop kerja dengan Intel i5, RAM 8GB, SSD 256GB, baterai tahan lama, ideal untuk pekerjaan kantoran dan kuliah.',
                'price': Decimal('6999999.99'),
                'stock': 12,
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed'
            },
            {
                'product_name': 'Monitor Gaming 27" 144Hz IPS',
                'category': 'Komputer & Laptop',
                'description': 'Monitor gaming dengan teknologi IPS, 144Hz refresh rate, response time 1ms, dan AMD FreeSync untuk pengalaman bermain smooth.',
                'price': Decimal('3499999.99'),
                'stock': 14,
                'image_url': 'https://images.unsplash.com/photo-1587993991335-351b2f09af6d'
            },
            {
                'product_name': 'Keyboard Mekanik RGB Gateron',
                'category': 'Komputer & Laptop',
                'description': 'Keyboard mekanik dengan switch Gateron, RGB lighting, hot-swappable, cocok untuk gaming dan typing profesional.',
                'price': Decimal('899999.99'),
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1587829191301-26ec2465a106'
            },
            {
                'product_name': 'Mouse Gaming Wireless Logitech',
                'category': 'Komputer & Laptop',
                'description': 'Mouse gaming wireless dengan sensor 25600 DPI, baterai tahan 70 jam, dan desain ergonomis untuk gaming marathon.',
                'price': Decimal('599999.99'),
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1527814050087-3793815479db'
            },
            {
                'product_name': 'Headset Gaming 7.1 Surround',
                'category': 'Komputer & Laptop',
                'description': 'Headset gaming dengan 7.1 virtual surround sound, noise cancellation mic, dan kenyamanan maksimal untuk gaming panjang.',
                'price': Decimal('1799999.99'),
                'stock': 18,
                'image_url': 'https://images.unsplash.com/photo-1487215078519-e21cc028cb29'
            }
        ]

        # Produk untuk Toko Python Elektronik
        toko_python_products = [
            {
                'product_name': 'Arduino Uno Rev3 Microcontroller',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Papan mikrokontroler Arduino Uno untuk pemula dan proyek robotika. Open-source dan kompatibel dengan berbagai sensor dan aktuator.',
                'price': Decimal('199999.99'),
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1515165835316-0a13e40d1f75'
            },
            {
                'product_name': 'Raspberry Pi 4 Model B 8GB',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Single board computer Raspberry Pi 4 dengan RAM 8GB, dual monitor support, cocok untuk IoT dan edge computing projects.',
                'price': Decimal('1299999.99'),
                'stock': 16,
                'image_url': 'https://images.unsplash.com/photo-1517059224940-d4af9eec41b7'
            },
            {
                'product_name': 'Sensor Ultrasonik HC-SR04',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Sensor jarak ultrasonik untuk robotika dan project IoT. Akurat, mudah digunakan dengan Arduino dan Raspberry Pi.',
                'price': Decimal('49999.99'),
                'stock': 100,
                'image_url': 'https://images.unsplash.com/photo-1553170506-9c186a1e2d58'
            },
            {
                'product_name': 'Motor DC 12V dengan Reducer',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Motor DC 12V dengan gear reducer untuk robotika, quadcopter, dan project DIY. Torsi tinggi dan RPM rendah untuk presisi.',
                'price': Decimal('299999.99'),
                'stock': 40,
                'image_url': 'https://images.unsplash.com/photo-1552820728-8ac41f1ce891'
            },
            {
                'product_name': 'Battery Jumper Starter 12V 600A',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Power bank mobil portable 12V 600A untuk emergency car starter. Dilengkapi LED flashlight dan USB charging ports.',
                'price': Decimal('599999.99'),
                'stock': 22,
                'image_url': 'https://images.unsplash.com/photo-1584622181563-430f63602d4b'
            },
            {
                'product_name': 'Kabel HDMI 2.1 8K 2 Meter',
                'category': 'Komponen & Aksesoris Elektronik',
                'description': 'Kabel HDMI 2.1 support 8K resolution dan 120fps. Durabel dengan shielding lengkap untuk transmisi video berkualitas tinggi.',
                'price': Decimal('249999.99'),
                'stock': 60,
                'image_url': 'https://images.unsplash.com/photo-1621905251918-48416bd8575a'
            }
        ]

        all_products = [
            ('sinar_baru_purwokerto', sinar_baru_products),
            ('banyumas_computer', banyumas_computer_products),
            ('toko_python_elektronik', toko_python_products)
        ]

        categories = {cat.category_name: cat for cat in Category.objects.all()}
        total_created = 0

        for username, products_list in all_products:
            brand = brands[username]
            self.stdout.write(self.style.SUCCESS(f"\n  👉 {brand.brand_name}:"))

            for prod_data in products_list:
                slug = slugify(prod_data['product_name'])

                product, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'brand_id': brand,
                        'category_id': categories[prod_data['category']],
                        'product_name': prod_data['product_name'],
                        'description': prod_data['description'],
                        'price': prod_data['price'],
                        'stock': prod_data['stock'],
                        'is_active': True,
                        'image': prod_data['image_url']
                    }
                )

                if created:
                    total_created += 1
                    price_str = f"Rp{prod_data['price']:,.0f}"
                    self.stdout.write(f"      ✓ {prod_data['product_name'][:50]:50} | {price_str}")

        self.stdout.write(
            self.style.SUCCESS(f"\n  📊 Total produk dibuat: {total_created}")
        )
