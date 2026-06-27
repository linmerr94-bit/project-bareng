import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

from master_products.models import Product

updates = {
    'AC Split 2 PK Inverter': 'https://static.retailworldvn.com/Products/Images/12178/320209/ac-split-daikin-inverter-2-pk-ftkq50uvm4-1-1.jpg',
    'Kulkas 2 Pintu Inverter 450L': 'https://www.static-src.com/wcsstore/Indraprastha/images/catalog/full//93/MTA-91531632/panasonic_kulkas-panasonic-2-pintu-bottom-freezer-nr-bx468vs-inverter-450-l_full01.jpg',
    'Mesin Cuci 8 Kg Full Automatic': 'https://cdn.polytron.co.id/public-assets/polytroncoid/2026/06/PAW28Y.webp',
    'Dispenser Air Panas Dingin Premium': 'https://www.qhomemart.com/wp-content/uploads/2022/12/6_11zon-18.jpg',
    'Battery Jumper Starter 12V 600A': 'https://modernautoparts.co.za/cdn/shop/files/JS600S_5_1024x.jpg?v=1751916340',
}

for name, url in updates.items():
    updated = Product.objects.filter(product_name=name).update(image=url)
    print(f"{'✓' if updated else '✗'} {name}")

print("\nDone!")