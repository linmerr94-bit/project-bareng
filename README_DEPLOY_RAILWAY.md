# Railway Deployment Guide

## 1. Push repository ke GitHub
Push semua perubahan ke repository GitHub Anda.

## 2. Buat project di Railway
- Buka Railway
- Pilih New Project
- Connect GitHub repository

## 3. Set environment variables
Tambahkan variabel berikut:
- SECRET_KEY=nilai-rahasia
- DEBUG=False
- ALLOWED_HOSTS=your-app.up.railway.app
- CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app

## 4. Build & Start
Railway akan menjalankan:
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn core_system.wsgi:application

## 5. Jalankan migrasi
Setelah deploy berhasil, jalankan:
- python manage.py migrate
- python manage.py createsuperuser
