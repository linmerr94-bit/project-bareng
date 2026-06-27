import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
django.setup()

from master_products.models import Product

updates = {
    'ASUS Gaming Laptop ROG': 'https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg?w=400',
    'Samsung Galaxy Buds3 Pro': 'https://images.pexels.com/photos/3780681/pexels-photo-3780681.jpeg?w=400',
    'ASUS VivoBook 15 OLED': 'https://images.pexels.com/photos/18105/pexels-photo.jpg?w=400',
    'Apple iPhone 15 Pro Max': 'https://images.pexels.com/photos/788946/pexels-photo-788946.jpeg?w=400',
    'Samsung Galaxy S24 Ultra': 'https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg?w=400',
    'MacBook Air 15 inch - Apple': 'https://images.pexels.com/photos/812264/pexels-photo-812264.jpeg?w=400',
    'Battery Jumper Starter 12V 600A': 'https://images.pexels.com/photos/3806288/pexels-photo-3806288.jpeg?w=400',
    'Motor DC 12V dengan Reducer': 'https://images.pexels.com/photos/257736/pexels-photo-257736.jpeg?w=400',
    'Sensor Ultrasonik HC-SR04': 'https://images.pexels.com/photos/163100/circuit-circuit-board-resistor-computer-163100.jpeg?w=400',
    'Arduino Uno Rev3 Microcontroller': 'https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?w=400',
    'Keyboard Mekanik RGB Gateron': 'https://images.pexels.com/photos/1772123/pexels-photo-1772123.jpeg?w=400',
    'Monitor Gaming 27" 144Hz IPS': 'https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg?w=400',
    'Laptop Gaming ASUS ROG 15.6"': 'https://images.pexels.com/photos/1038916/pexels-photo-1038916.jpeg?w=400',
    'Dispenser Air Panas Dingin Premium': 'https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?w=400',
    'Mesin Cuci 8 Kg Full Automatic': 'https://images.pexels.com/photos/5591458/pexels-photo-5591458.jpeg?w=400',
    'AC Split 2 PK Inverter': 'https://images.pexels.com/photos/4149040/pexels-photo-4149040.jpeg?w=400',
    'Kulkas 2 Pintu Inverter 450L': 'https://images.pexels.com/photos/2724749/pexels-photo-2724749.jpeg?w=400',
}

for name, url in updates.items():
    updated = Product.objects.filter(product_name=name).update(image=url)
    print(f"{'✓' if updated else '✗'} {name}")

print("\nDone!")