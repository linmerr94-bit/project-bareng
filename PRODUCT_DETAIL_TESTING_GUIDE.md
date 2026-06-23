# 🧪 PRODUCT DETAIL PAGE - COMPREHENSIVE TESTING GUIDE

**Created**: 2026-06-09  
**Status**: ✅ READY FOR TESTING  
**Database Status**: ✅ Seed data loaded (8 products, 4 brands, 3 categories)

---

## 📊 CURRENT DATABASE STATE

### Seed Data Loaded:
- ✅ **3 Categories**: Elektronik, Pakaian, Aksesoris
- ✅ **4 Brands** (All APPROVED): TechHub Indonesia, StylePro Boutique, Aksesori Prime + 1 other
- ✅ **8 Products** (All Active): With prices, stock, images, descriptions, and proper ForeignKey relationships

### Sample Products Created:
1. **Laptop Gaming Pro 15"** - Rp 13,000,000 | Stock: 15
2. **Smartphone XZB 13 Pro** - Rp 9,000,000 | Stock: 25
3. **Kemeja Katun Premium Pria** - Rp 350,000 | Stock: 50
4. **Dress Kasual Wanita** - Rp 450,000 | Stock: 40
5. **Tas Tangan Kulit Asli** - Rp 1,300,000 | Stock: 20
6. **Dompet Kulit Bifold** - Rp 550,000 | Stock: 35
7. **Headphone Wireless Noise Cancelling** - Rp 2,500,000 | Stock: 18
8. Plus 1 more product

---

## 🚀 START TESTING

### **STEP 1: Start Django Development Server**

```bash
# Terminal 1 - Start the development server
python manage.py runserver

# OR use the VS Code task
# Command: 🚀 Run Django Server
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### **STEP 2: Access Homepage**

```
http://127.0.0.1:8000/
```

**Should See:**
- ✅ Product grid with all 8 products
- ✅ Each product card shows: image, name, price, category
- ✅ No console errors in terminal

---

## 🧪 TEST SCENARIO 1: BASIC PRODUCT DETAIL PAGE LOADING

### **Test 1.1: Click on First Product**

**Action:**
1. Go to `http://127.0.0.1:8000/`
2. Click on first product card (Laptop Gaming Pro 15")

**Expected Result:**
```
✅ URL changes to: http://127.0.0.1:8000/product/laptop-gaming-pro-15/
✅ Page loads without 404 error
✅ Product detail page displays
```

### **Test 1.2: Verify URL Format**

**Check:**
1. Look at the address bar
2. URL should be `/product/<product-slug>/` format
3. Example: `/product/laptop-gaming-pro-15/`

**Expected:**
```
✅ URL is slug-based (readable, not numeric)
✅ URL contains only lowercase letters, numbers, hyphens
✅ URL matches: /product/smartphone-xzb-13-pro/
```

### **Test 1.3: Direct URL Access**

**Action:**
1. Manually navigate to: `http://127.0.0.1:8000/product/laptop-gaming-pro-15/`

**Expected Result:**
```
✅ Page loads directly without issues
✅ Correct product displays
```

### **Test 1.4: Invalid Slug**

**Action:**
1. Navigate to: `http://127.0.0.1:8000/product/non-existent-product/`

**Expected Result:**
```
✅ Shows 404 error page (not 500)
✅ User-friendly error message
```

---

## 🧪 TEST SCENARIO 2: PRODUCT INFORMATION DISPLAY

### **Test 2.1: Check Product Name**

**Action:**
1. Open product detail page for Laptop Gaming Pro
2. Look at page title/heading

**Expected:**
```
✅ Page title shows: "Laptop Gaming Pro 15"
✅ Heading <h1> displays product name
```

### **Test 2.2: Check Product Price**

**Action:**
1. Look for price section on product detail page

**Expected:**
```
✅ Price displays: "Rp13,000,000"
✅ Format is correct with thousands separator
✅ Currency symbol "Rp" is present
```

### **Test 2.3: Check Stock Status**

**Action:**
1. For product with stock > 10 (e.g., Laptop with 15 items):
   - Look for stock status badge

**Expected:**
```
✅ Badge shows: "✓ Stok Tersedia" (green)
```

**Action 2:**
1. For product with stock 1-9 (test with any matching product):
   - Look for stock status badge

**Expected:**
```
✅ Badge shows: "⚠ Stok Terbatas (X unit)" (orange)
```

**Action 3:**
1. Check product with 0 stock (if available):
   - Look for stock status badge

**Expected:**
```
✅ Badge shows: "✗ Stok Habis" (red)
✅ "Tambah ke Keranjang" button is DISABLED
```

### **Test 2.4: Check Category Display**

**Action:**
1. Look for category information on product detail page

**Expected:**
```
✅ Shows: "🏷 Elektronik" (for electronics)
✅ Shows: "🏷 Pakaian" (for clothing)
✅ Shows: "🏷 Aksesoris" (for accessories)
```

### **Test 2.5: Check Seller/Brand Information**

**Action:**
1. Look for "PENJUAL" (Seller) section
2. Check brand name and verification status

**Expected:**
```
✅ Shows: "TechHub Indonesia" / "StylePro Boutique" / "Aksesori Prime"
✅ Shows: "✓ Seller Terverifikasi" (green checkmark)
✅ Status should be "Terverifikasi" (Verified) because seed sets status='APPROVED'
```

### **Test 2.6: Check Product Description**

**Action:**
1. Scroll down on product detail page
2. Look for description section

**Expected:**
```
✅ Description text is visible
✅ Text is properly formatted (no HTML tags showing)
✅ Multiple paragraphs/sections display correctly
```

### **Test 2.7: Check Product Image**

**Action:**
1. Look at product image on detail page

**Expected:**
```
✅ Image displays (or fallback placeholder if no image)
✅ Image is properly sized/responsive
✅ No broken image icons (❌)
```

---

## 🧪 TEST SCENARIO 3: NAVIGATION & BUTTONS

### **Test 3.1: Breadcrumb Navigation**

**Action:**
1. Look for breadcrumb at top: "Home / Category / Product Name"
2. Click on "Katalog" link

**Expected:**
```
✅ Breadcrumb displays: "🏠 Katalog / Elektronik / Laptop Gaming Pro 15""
✅ Clicking "Katalog" takes you back to product list
```

### **Test 3.2: Kembali ke Katalog Button**

**Action:**
1. Scroll to bottom of page
2. Look for "Kembali ke Katalog" button
3. Click it

**Expected:**
```
✅ Button exists and is clickable
✅ Clicking it returns to product list page
✅ URL changes back to http://127.0.0.1:8000/
```

### **Test 3.3: Add to Cart Button (Logged Out)**

**Action:**
1. Make sure you're NOT logged in
2. Look for "Tambah ke Keranjang" button
3. Hover over it

**Expected:**
```
✅ Button is visible
✅ Clicking it should prompt login
```

---

## 🧪 TEST SCENARIO 4: AUTHENTICATION & SECURITY

### **Test 4.1: CSRF Token Check**

**Action:**
1. Open browser Developer Tools (F12)
2. Click on Network tab
3. Click "Tambah ke Keranjang" button
4. Look at the POST request

**Expected:**
```
✅ POST request includes CSRF token
✅ Request succeeds (200 or 302, not 403)
```

### **Test 4.2: Login Redirect (Optional)**

**Action:**
1. Make sure you're logged OUT
2. Click "Tambah ke Keranjang" button
3. Observe redirect

**Expected:**
```
✅ Redirects to login page
✅ After login, goes back to product detail page
```

---

## 🧪 TEST SCENARIO 5: RESPONSIVE DESIGN

### **Test 5.1: Desktop View (1920x1080)**

**Action:**
1. Open DevTools → Device Toolbar (Ctrl+Shift+M)
2. Select "Desktop" (1920x1080)
3. View product detail page

**Expected:**
```
✅ 2-column layout (image left, info right)
✅ All elements properly aligned
✅ No horizontal scrollbar
✅ Text is readable
```

### **Test 5.2: Tablet View (768x1024)**

**Action:**
1. DevTools → Select "Tablet" (e.g., iPad)
2. View product detail page

**Expected:**
```
✅ Layout adapts to tablet size
✅ Image and info stack nicely
✅ All buttons are clickable (not too small)
```

### **Test 5.3: Mobile View (375x667)**

**Action:**
1. DevTools → Select "Mobile" (e.g., iPhone SE)
2. View product detail page

**Expected:**
```
✅ Single-column layout
✅ Image full width
✅ All info stacks vertically
✅ Buttons are full width and easily clickable
✅ No content overflow
```

---

## 🧪 TEST SCENARIO 6: MULTIPLE PRODUCTS

### **Test 6.1: Click Different Products**

**Action:**
1. Go back to homepage
2. Click on different products:
   - Smartphone (Elektronik)
   - Kemeja (Pakaian)
   - Tas Tangan (Aksesoris)

**Expected:**
```
✅ Each product has correct slug in URL
✅ Product-specific information displays correctly
✅ No errors in console
✅ Category matches the product type
```

### **Test 6.2: URL Uniqueness**

**Action:**
1. Open two products in different tabs
2. Compare URLs in address bars

**Expected:**
```
✅ Each product has unique slug
✅ URLs are different
✅ Product names match their URLs
```

---

## 🧪 TEST SCENARIO 7: ERROR HANDLING

### **Test 7.1: Product Not Found**

**Action:**
1. Navigate to: `http://127.0.0.1:8000/product/does-not-exist/`

**Expected:**
```
✅ Shows 404 Not Found (not 500 error)
✅ Error message is user-friendly
✅ Page offers option to go back or browse
```

### **Test 7.2: Inactive Product**

**Action:**
1. Manually mark a product as `is_active=False` in Django admin
2. Try to access its detail page

**Expected:**
```
✅ Shows 404 (product is filtered out)
✅ Does not show inactive products
```

### **Test 7.3: Unapproved Brand**

**Action:**
1. Manually mark a brand as `status='pending'` in Django admin
2. Try to access a product from that brand

**Expected:**
```
✅ Shows 404 (brand is not approved)
✅ Does not show products from unapproved brands
```

---

## 🧪 TEST SCENARIO 8: TEMPLATE CONSISTENCY

### **Test 8.1: Template Variables**

**Action:**
1. View page source (Ctrl+U)
2. Search for product name

**Expected:**
```
✅ Product name appears in <title> tag
✅ Product name in <h1> heading
✅ No error messages in HTML
✅ No placeholder text like {{ product.name }}
```

### **Test 8.2: Stock Badge Colors**

**Action:**
1. Check products with different stock levels
2. Observe badge colors

**Expected:**
- Stock > 10: 🟢 **Green** badge (Tersedia)
- Stock 1-9: 🟠 **Orange** badge (Terbatas)
- Stock = 0: 🔴 **Red** badge (Habis)

### **Test 8.3: Price Formatting**

**Action:**
1. Check various products with different prices
2. Verify price display format

**Expected:**
```
✅ Rp9,000,000 (with thousands separator)
✅ Rp13,000,000 (correct formatting)
✅ Rp2,500,000 (consistent across all products)
✅ No unwanted decimals
```

---

## 📋 MANUAL VERIFICATION CHECKLIST

Print this out and check off each item:

### **Basic Functionality**
- [ ] Product detail page loads from homepage click
- [ ] URL uses slug format (readable, not ID)
- [ ] No 404 or 500 errors on valid products
- [ ] 404 error shown for invalid/non-existent products
- [ ] Direct URL access works (can paste URL directly)

### **Content Display**
- [ ] Product name displays
- [ ] Product price displays correctly (Rp format)
- [ ] Product image displays (or placeholder)
- [ ] Category badge shows correct category
- [ ] Stock status badge shows with correct color
- [ ] Stock quantity displayed
- [ ] Seller/brand name displays
- [ ] Seller verification status shows
- [ ] Product description displays
- [ ] Breadcrumb navigation shows

### **Navigation**
- [ ] "Kembali ke Katalog" button works
- [ ] Breadcrumb links work (Katalog, Category)
- [ ] Back button in browser works

### **User Interface**
- [ ] Page layout is clean and professional
- [ ] Colors are consistent (indigo/slate theme)
- [ ] Icons display correctly
- [ ] Responsive on mobile/tablet/desktop
- [ ] No text overflow or layout issues
- [ ] Buttons are clearly clickable

### **Stock & Purchase**
- [ ] Stock status correctly shows available/limited/out
- [ ] "Tambah ke Keranjang" button visible (for logged-in users)
- [ ] Button disabled when stock is 0
- [ ] Add to cart button leads to cart page

### **Security**
- [ ] CSRF token present in forms
- [ ] No sensitive data in URL
- [ ] Proper authentication checks

### **Performance**
- [ ] Page loads quickly (< 2 seconds)
- [ ] No console JavaScript errors
- [ ] No console warning messages (other than expected)
- [ ] Images load properly

---

## 🐛 TROUBLESHOOTING

### **Issue: 404 Error on Product Detail**

**Solution:**
1. Check if Django server is running: `python manage.py runserver`
2. Verify URL pattern matches in `master_products/urls.py`: `path('product/<slug:slug>/', ...)`
3. Verify slug exists: `python manage.py dbshell` → `SELECT slug FROM master_products_product;`

### **Issue: Product Information Not Displaying**

**Solution:**
1. Check template variables in `master_products/views.py` - all context keys
2. Verify template file path: `master_products/templates/master_products/product_detail.html`
3. Check for template syntax errors (undefined variables)

### **Issue: Price Not Formatted**

**Solution:**
1. Verify in views.py: `'price_formatted': f"Rp{product.price:,.0f}"`
2. Check template uses `price_formatted` not `price`

### **Issue: Stock Badge Not Showing Correct Color**

**Solution:**
1. Verify stock calculation logic in views.py
2. Check Tailwind CSS classes applied to badge

### **Issue: Image Not Displaying**

**Solution:**
1. Check if image file exists in media directory
2. Verify Media URL is configured in settings.py
3. Check image field in model has proper path

### **Issue: Add to Cart Button Not Working**

**Solution:**
1. Verify add_to_cart view exists in views.py
2. Check add_to_cart URL is registered in urls.py
3. Verify cart/cartitem models are defined

---

## 📞 QUICK COMMANDS

```bash
# Start Django server
python manage.py runserver

# Load seed data
python manage.py seed_sample_data

# Check Django configuration
python manage.py check

# Access Django shell
python manage.py shell

# View database
python manage.py dbshell
```

---

## 📝 TEST REPORT TEMPLATE

After testing, document results:

```
## Product Detail Page - Test Report
**Date**: [Date]
**Tester**: [Name]
**Status**: [PASS / FAIL / PARTIAL]

### Tests Passed:
- ✅ [Test name]
- ✅ [Test name]

### Tests Failed:
- ❌ [Test name]
  Issue: [Description]
  
### Issues Found:
1. [Issue description]
2. [Issue description]

### Recommendations:
1. [Recommendation]
2. [Recommendation]
```

---

**Status**: ✅ COMPREHENSIVE TESTING GUIDE COMPLETE  
**Ready for**: Manual testing by developer/QA team  
**Next Step**: Execute tests and document results

---
