# 🚀 DEPLOY RAILWAY - PANDUAN STEP BY STEP

## TAHAP 1: LOGIN GITHUB & AUTHORIZE RAILWAY ✅ SUDAH SAMPAI SINI

Halaman sekarang ada di: **GitHub Login**

### LANGKAH BERIKUT:
1. **Di halaman login GitHub, isi:**
   - Username: `linmerr94-bit` (atau email yang terdaftar)
   - Password: (password GitHub Anda)
   
2. **Klik "Sign in"**

3. **Railway akan minta authorize** - Klik **"Authorize railwayapp"**

---

## TAHAP 2: DASHBOARD RAILWAY

Setelah authorize, Anda akan masuk ke Dashboard Railway.

### LANGKAH DI DASHBOARD:
1. **Klik "New Project"** (tombol besar di tengah)
2. Pilih **"Deploy from GitHub Repo"**
3. Cari repository: **`linmerr94-bit/project-bareng`**
4. Klik **"Configure GitHub App"** jika perlu authorize
5. Pilih repository, klik **"Deploy"**

---

## TAHAP 3: SETUP ENVIRONMENT VARIABLES

Setelah connected, Anda akan di halaman project baru.

### LANGKAH:
1. Klik tab **"Variables"** (atau settings)
2. Klik **"New Variable"** dan masukkan:

```
SECRET_KEY = django-insecure-uzkeyl89rucd-y1p$&a6u@(h1g$pn9abir-=qwhr46t3l2ne@f
DEBUG = False
ALLOWED_HOSTS = *
CSRF_TRUSTED_ORIGINS = https://*.up.railway.app
USE_POSTGRES = True
```

3. **PENTING**: Klik **"Add Plugin"** → Pilih **"PostgreSQL"**
   - Railway otomatis akan generate `DATABASE_URL`

---

## TAHAP 4: DEPLOY

1. Klik **"Deploy"** atau setup akan auto-deploy
2. **Tunggu 3-5 menit** sampai build selesai
3. Status akan berubah jadi **"ONLINE"** dan berwarna hijau
4. Anda akan diberikan URL aplikasi (misal: `volta-prod.up.railway.app`)

---

## TAHAP 5: JALANKAN MIGRASI KRITIS!

Ini SANGAT PENTING. Tanpa migrasi, database tidak akan siap.

### LANGKAH:
1. Di Railway dashboard, klik project Anda
2. Pergi ke tab **"Deploy"** → Klik **"Shell"** atau **"Terminal"**
3. Jalankan perintah berikut (satu per satu):

```bash
python manage.py migrate
python manage.py createsuperuser
```

Untuk `createsuperuser`:
- Username: `admin`
- Email: `admin@example.com`
- Password: (buat password yang kuat)

---

## TAHAP 6: TEST APLIKASI

1. Buka URL aplikasi Anda
2. Login dengan:
   - Username: `admin`
   - Password: (yang Anda buat tadi)
3. Selesai! 🎉

---

## TROUBLESHOOTING

### Error: "No such table: auth_user"
→ Jalankan di Railway Shell:
```bash
python manage.py migrate
```

### Error: "DEBUG must be False"
→ Pastikan di Variables: `DEBUG = False` (bukan True)

### Static files tidak tampil (CSS/JS hilang)
→ Jalankan di Railway Shell:
```bash
python manage.py collectstatic --noinput
```

### Build gagal?
→ Cek "Build Logs" di Railway dashboard untuk melihat error

---

## HASIL AKHIR
- URL aplikasi: `https://your-app.up.railway.app`
- Database: PostgreSQL (managed by Railway)
- Static files: WhiteNoise (auto-served)
- SSL/HTTPS: Auto provided by Railway

**SELESAI! 🚀**
