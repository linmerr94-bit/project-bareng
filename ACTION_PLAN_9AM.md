# 🚨 JAM 8:45 AM - FINAL ACTION PLAN

**Status**: 9 Critical Issues Found → All Fixed Code Ready  
**Est. Time**: 15-20 minutes  
**Testing**: Ready for 9 AM Live Test  

---

## ⚡ QUICK START - FOLLOW THESE STEPS EXACTLY:

### STEP 1: Add Missing Imports (30 seconds) ✅

**File**: `master_products/views.py` (Line 4)

Replace THIS:
```python
from django.http import HttpResponseForbidden
```

With THIS:
```python
from django.http import HttpResponseForbidden, JsonResponse
```

---

### STEP 2: Add Missing Views (3 minutes)

**File**: `master_products/views.py` (At the END of file, before any admin sections)

**COPY ALL THIS CODE** from `HOTFIX_COMPLETE_CODE.md` section:
- **"PRIORITY 1: FIX & AKTIFKAN FITUR PROFIL USER"** → Copy all 3 view functions:
  1. `user_profile()`
  2. `edit_profile()`
  3. `change_password()`

- **"PRIORITY 2: CART & CHECKOUT"** → Copy these view functions:
  1. `update_cart_item()`
  2. `remove_from_cart()`
  3. `checkout_view()` (REPLACE existing if any)

- **"PRIORITY 3: KOMUNIKASI & CS"** → Copy these view functions:
  1. `get_store_whatsapp()`
  2. `submit_care_hub_inquiry()`

---

### STEP 3: Create 3 New Profile Templates (2 minutes)

**COPY 3 template files** dari `HOTFIX_COMPLETE_CODE.md`:

1. **CREATE**: `master_products/templates/master_products/user_profile.html`
2. **CREATE**: `master_products/templates/master_products/edit_profile.html`
3. **CREATE**: `master_products/templates/master_products/change_password.html`

(Copy full HTML content dari HOTFIX_COMPLETE_CODE.md)

---

### STEP 4: Update URLs (1 minute)

**File**: `master_products/urls.py` (Add at the END of urlpatterns, around line 50)

**ADD THIS**:
```python
    # ==================== CART API ENDPOINTS ====================
    path('api/update-cart/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # ==================== CUSTOMER SERVICE API ====================
    path('api/store/<int:store_id>/whatsapp/', views.get_store_whatsapp, name='get_store_whatsapp'),
    path('api/care-hub/submit/', views.submit_care_hub_inquiry, name='submit_care_hub_inquiry'),
    
    # ==================== USER PROFILE ====================
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
```

---

### STEP 5: Add Product Model Fields (1 minute + Migration)

**File**: `master_products/models.py` (Find Product model, add after `stock` field)

**ADD THIS**:
```python
    # Rating dari reviews customer
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        db_column='rating',
        help_text="Rating rata-rata dari customer reviews (0.0-5.0)"
    )
    
    # Jumlah review
    review_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        db_column='review_count',
        help_text="Jumlah customer yang review produk ini"
    )
```

**Then RUN**:
```bash
python manage.py makemigrations master_products
python manage.py migrate
```

---

### STEP 6: Fix Template Image References (3 minutes)

**6 FILES need to be fixed** - Replace `product_image` with `image`:

#### File 1: `master_products/templates/master_products/cart.html` (Line ~432)
```html
<!-- OLD -->
{% if item.product_id.product_image %}
    <img src="{{ item.product_id.product_image.url }}" ...>

<!-- NEW -->
{% if item.product_id.image %}
    <img src="{{ item.product_id.image.url }}" ...>
```

#### File 2: `master_products/templates/master_products/checkout.html` (Line ~625)
```html
<!-- Same replacement as above -->
```

#### File 3: `master_products/templates/master_products/checkout_detailed.html` (Line ~621)
#### File 4: `master_products/templates/master_products/payment_gateway.html` (Line ~543)
#### File 5: `master_products/templates/master_products/payment_confirmation.html` (Line ~280)
#### File 6: `master_products/templates/master_products/order_detail.html` (Line ~336)

(Same replacement pattern for all 6 files)

---

### STEP 7: Update store_detail.html WhatsApp Button (1 minute)

**File**: `master_products/templates/master_products/store_detail.html`

Find the WhatsApp button (around line 450) and REPLACE:
```html
<!-- OLD (Static) -->
<a href="https://wa.me/62{{ store.user.phone }}" target="_blank" class="btn-contact">
    <i class="fab fa-whatsapp"></i> Hubungi Toko
</a>

<!-- NEW (Dynamic) -->
<button id="btn-whatsapp-contact" class="btn-contact" onclick="contactStoreViaWhatsApp()">
    <i class="fab fa-whatsapp"></i> Hubungi Toko
</button>

<script>
function contactStoreViaWhatsApp() {
    const storeId = '{{ store.brand_id }}';
    
    fetch(`/api/store/${storeId}/whatsapp/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.open(data.whatsapp_url, '_blank');
            } else {
                alert('❌ Nomor WhatsApp tidak tersedia. Silakan hubungi CS VOLTA.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Terjadi kesalahan. Silakan coba lagi.');
        });
}
</script>
```

---

### STEP 8: Update login.html VOLTA Care Hub (1 minute)

**File**: `master_products/templates/master_products/login.html`

Find the VOLTA Care Hub JavaScript section and REPLACE dengan code dari `HOTFIX_COMPLETE_CODE.md` - section **"PRIORITY 3: KONEKSIKAN BACKEND WIDGET KOMUNIKASI"** - bagian "File 4: Update login.html"

---

### STEP 9: Verify DRF Installation (30 seconds)

**File**: `core_system/settings.py`

Ensure `INSTALLED_APPS` has:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',  # ← Must be here
    ...
]
```

If not present, ADD IT.

---

### STEP 10: Run Final Tests (5 minutes)

```bash
# Terminal 1: Check for errors
python manage.py check

# Terminal 2: Run server
python manage.py runserver

# Terminal 3: Test URLs in browser/curl
curl http://localhost:8000/profile/
curl http://localhost:8000/profile/edit/
curl http://localhost:8000/cart/
curl http://localhost:8000/checkout/
curl http://localhost:8000/login/
```

**Expected**: All pages load without 500 errors ✅

---

---

## 🎯 COMPLETE CODE BLOCKS - COPY-PASTE

All complete, production-ready code is in: **`HOTFIX_COMPLETE_CODE.md`**

Reference the sections:
- **PRIORITY 1**: User Profile Views + Templates
- **PRIORITY 2**: Cart & Checkout Views + Models
- **PRIORITY 3**: WhatsApp & Care Hub Views
- **PRIORITY 4**: Import & Model Consolidation

---

## ⏱️ TIMING

| Step | Time | Cumulative |
|------|------|-----------|
| 1. Imports | 30s | 0:30 |
| 2. Add Views | 3min | 3:30 |
| 3. Templates | 2min | 5:30 |
| 4. URLs | 1min | 6:30 |
| 5. Model Fields + Migrate | 2min | 8:30 |
| 6. Fix 6 Template Images | 3min | 11:30 |
| 7. WhatsApp Button | 1min | 12:30 |
| 8. Care Hub JS | 1min | 13:30 |
| 9. DRF Check | 30s | 14:00 |
| 10. Final Tests | 5min | 19:00 |
| **TOTAL** | | **~19 min** |

**Target**: Finish by 8:55 AM ✅

---

---

## 🚨 IF SOMETHING BREAKS

### Error: "No module named 'rest_framework'"
**Fix**: `pip install djangorestframework`

### Error: "JsonResponse not imported"
**Fix**: Check Step 1 - add import

### Error: "NoReverseMatch at /profile/"
**Fix**: Check Step 4 - add URL patterns

### Error: "product_image does not exist"
**Fix**: Check Step 6 - fix template references

### Error: "Cannot add non-nullable field without default"
**Fix**: When running migrate, use `--fake` if needed:
```bash
python manage.py migrate --fake
```

---

---

## ✅ LIVE TEST SCENARIOS (9 AM)

### Test 1: User Profile
- Login → Click Profile → Should show `/profile/` page ✅
- Click Edit → Edit name/email/phone → Save → Should update ✅
- Click Change Password → Change password → Should logout & require re-login ✅

### Test 2: Shopping Cart
- Add product to cart → Click cart icon → Should show items ✅
- Update quantity → Should call `/api/update-cart/` → Qty updates ✅
- Remove item → Should call `/api/remove-from-cart/<id>/` → Item removed ✅
- Proceed to checkout → Should show 2 orders (if multi-vendor) ✅

### Test 3: Communication
- Store page → Click "Hubungi Toko" → Should open WhatsApp ✅
- Login page → Click Care Hub button → Should show accordion ✅
- Submit question → Should call `/api/care-hub/submit/` → Success message ✅

---

**Ready for 9 AM launch! Go go go!** 🚀

