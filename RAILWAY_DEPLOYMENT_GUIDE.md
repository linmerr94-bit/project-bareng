# PANDUAN DEPLOY KE RAILWAY (LANGKAH DEMI LANGKAH)

## ✅ Yang sudah siap di project ini:
- Procfile (untuk perintah start)
- requirements.txt (dengan semua dependensi)
- runtime.txt (Python 3.13.7)
- railway.toml (konfigurasi build & deploy)
- .env.example (template variabel)
- Settings.py dengan support DATABASE_URL & WhiteNoise

## 📋 LANGKAH DEPLOY DI RAILWAY

### 1. Buka Railway
- Buka: https://railway.app
- Login dengan akun Anda (atau signup jika belum ada)

### 2. Buat New Project
- Klik **"New Project"**
- Pilih **"Deploy from GitHub repo"**

### 3. Connect GitHub
- Pilih repository: `linmerr94-bit/project-bareng`
- Klik **"Connect"**
- Authorize Railway untuk akses GitHub

### 4. Set Environment Variables
Setelah repo terhubung, pergi ke **"Variables"** tab:

```
SECRET_KEY=django-insecure-uzkeyl89rucd-y1p$&a6u@(h1g$pn9abir-=qwhr46t3l2ne@f
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=https://*.up.railway.app
USE_POSTGRES=True
DATABASE_URL=(akan terisi otomatis dari PostgreSQL plugin)
```

### 5. Tambahkan PostgreSQL Database
- Klik **"Add Plugin"**
- Pilih **"PostgreSQL"**
- Railway otomatis akan generate `DATABASE_URL`

### 6. Konfigurasi Build & Deploy
Settings akan biasanya otomatis terdeteksi dari Procfile, tapi pastikan:
- **Start Command**: `gunicorn core_system.wsgi:application`
- **Build Command**: `pip install -r requirements.txt`

### 7. Deploy!
- Klik **"Deploy"**
- Tunggu proses build selesai (3-5 menit)
- URL aplikasi akan muncul di dashboard Railway (contoh: `your-app.up.railway.app`)

### 8. Jalankan Migrasi (Critical!)
Setelah deploy berhasil:
- Pergi ke tab **"Deploy"** → **"View Logs"** atau klik **"Shell"**
- Jalankan:
  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  ```

### 9. Test Aplikasi
- Buka URL aplikasi: `https://your-app.up.railway.app`
- Login dengan superuser yang baru dibuat

## 🔧 Troubleshooting

### Error: "No such table: auth_user"
→ Jalankan migrasi di Railway shell:
```bash
python manage.py migrate
```

### Error: "DEBUG must be False in production"
→ Pastikan di Variables: `DEBUG=False`

### Error: "Static files not found (CSS/JS)"
→ Jalankan di Railway shell:
```bash
python manage.py collectstatic --noinput
```

## 📞 Need Help?
- Railway Dashboard: https://railway.app
- Django Docs: https://docs.djangoproject.com
- Railway Docs: https://docs.railway.app
