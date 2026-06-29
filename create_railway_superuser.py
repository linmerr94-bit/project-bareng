#!/usr/bin/env python
"""
Script untuk membuat superuser di Railway environment
Jalankan: python manage.py shell < create_railway_superuser.py
"""
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# Data superuser
email = "admin@volta.local"
username = "admin"
password = "admin123"  # Ganti ini dengan password yang lebih kuat!

# Check jika user sudah ada
if User.objects.filter(username=username).exists():
    print(f"✓ User '{username}' sudah ada!")
    user = User.objects.get(username=username)
else:
    # Create superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✓ Superuser '{username}' berhasil dibuat!")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"\n📌 SEGERA GANTI PASSWORD DI ADMIN PANEL!")

print(f"\n✓ Admin URL: https://web-production-af2b5.up.railway.app/admin/")
print(f"✓ Login dengan:")
print(f"  Username: {username}")
print(f"  Password: {password}")
