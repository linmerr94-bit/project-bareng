#!/usr/bin/env python
"""
Script untuk membuat superuser test untuk B2B testing
"""
import os
import sys
import django
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_system.settings')
sys.path.insert(0, 'D:\\PROJEK UAS E-COMMERCE')
django.setup()

# Create superuser
username = 'testadmin'
email = 'admin@volta.com'
password = 'admin123'

try:
    user = User.objects.create_superuser(username, email, password)
    print(f"✓ Superuser '{username}' berhasil dibuat")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
    print(f"\nGunakan akun ini untuk login dan test fitur B2B")
except Exception as e:
    print(f"✗ Error: {e}")
