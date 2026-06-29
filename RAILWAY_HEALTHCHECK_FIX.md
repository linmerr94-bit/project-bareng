# TROUBLESHOOT: Railway Healthcheck Failure

## 🔍 MASALAH UMUM DAN SOLUSI

### MASALAH 1: Port Mismatch
**Symptom**: Healthcheck failure
**Cause**: Railway mengirim healthcheck ke port yang salah

**Solusi**:
Di `settings.py`, tambahkan di bawah SECRET_KEY:

```python
PORT = os.getenv('PORT', '8000')
```

Di `Procfile`, ubah menjadi:

```
web: gunicorn core_system.wsgi:application --bind 0.0.0.0:$PORT --log-file -
```

---

### MASALAH 2: Database Connection Timeout
**Symptom**: App crash saat startup
**Cause**: Database belum siap atau DATABASE_URL salah

**Solusi**:
1. Di Railway dashboard, pastikan PostgreSQL plugin sudah ditambahkan
2. Verify di Variables tab: `DATABASE_URL` harus terisi otomatis
3. Format harus: `postgresql://user:pass@host:port/dbname`

---

### MASALAH 3: DEBUG Mode Masih True
**Symptom**: Server crash atau error response
**Cause**: DEBUG=True di production

**Solusi**:
Di Variables, pastikan: `DEBUG=False`

---

### MASALAH 4: Static Files Error
**Symptom**: 500 Internal Server Error
**Cause**: Static files tidak bisa di-load

**Solusi**:
Di Railway Shell, jalankan:
```bash
python manage.py collectstatic --noinput
```

---

## 🛠️ QUICK FIX CHECKLIST

### Step 1: Update Procfile
```
web: gunicorn core_system.wsgi:application --bind 0.0.0.0:$PORT --log-file - --timeout 60
```

### Step 2: Update settings.py
Tambahkan di awal file (setelah import):
```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# CRITICAL: Railway passes PORT as environment variable
PORT = int(os.getenv('PORT', 8000))
```

### Step 3: Pastikan di Variables:
```
PORT = 8000
DEBUG = False
ALLOWED_HOSTS = *
DATABASE_URL = [auto-filled by Railway PostgreSQL]
```

### Step 4: Di Railway Shell:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 5: Redeploy
- Klik "Redeploy" atau push ke GitHub lagi

---

## 📊 LOG YANG BIASANYA MUNCUL

### ✅ SUKSES:
```
Uvicorn running on http://0.0.0.0:8000
Application startup complete
```

### ❌ GAGAL - Port Error:
```
Address already in use
Cannot bind to port 8000
```

### ❌ GAGAL - Database Error:
```
psycopg2.OperationalError: connection failed
ERROR: django.db.utils.OperationalError
```

### ❌ GAGAL - DEBUG Mode:
```
DEBUG=True is not allowed in production
```

---

## 🚀 COMPLETE SOLUTION

Jika masih gagal, ikuti langkah ini:

1. **Update Procfile** ← PENTING
2. **Update settings.py** untuk read PORT env var
3. **Verify Variables** di Railway
4. **Run migrations** di Shell
5. **Redeploy** dari dashboard
6. **Check logs** setelah deploy

Paste log error Anda di sini dan saya akan bantu analisis lebih lanjut!
