# 🧪 ADD TO CART - QUICK TESTING GUIDE

**Status**: ✅ **READY TO TEST**  
**Time to First Test**: 5 minutes

---

## 🚀 START TESTING NOW

### **STEP 1: Start Django Server**
```bash
python manage.py runserver
```

### **STEP 2: Open Browser**
```
http://127.0.0.1:8000/
```

### **STEP 3: Test Scenario - Not Logged In**
1. **Verify Not Logged In**: Look at navbar - should NOT see username
2. **Click Product**: Click any product (e.g., "Laptop Gaming Pro 15")
3. **Check Button Text**: Should show **"Login untuk Membeli"** (not "Tambah ke Keranjang")
4. **Click Button**: Click "Login untuk Membeli"
5. **Expected**: Redirected to **login page** ✅

### **STEP 4: Login**
1. **Enter Credentials**: 
   - Username: `vendor_elektronik` or any existing user
   - Password: (whatever was set during seed data)
2. **Click Login**
3. **Expected**: Redirected to product detail page ✅

### **STEP 5: Test Scenario - Logged In**
1. **Back to Product**: Already at product detail page
2. **Check Button**: Should now show **"Tambah ke Keranjang"** ✅
3. **Click Button**
4. **Expected Results**:
   - ✅ Success message appears (green)
   - ✅ Message says: "✅ 'Product Name' berhasil ditambahkan ke keranjang! (Qty: 1)"
   - ✅ Redirected to cart page

### **STEP 6: Verify Cart Page**
1. **At Cart Page**: URL should be `/cart/`
2. **Check Product**: Product should appear in list
3. **Check Quantity**: Should show qty=1
4. **Check Price**: Should show Rp format price

### **STEP 7: Test Quantity Increment**
1. **Back to Same Product**: Click back button or product link
2. **Click "Tambah ke Keranjang" Again**
3. **Expected**:
   - ✅ Success message with qty=1 (not qty=2)
   - ✅ Redirected to cart
   - ✅ Same product now shows qty=2 (quantity incremented)

### **STEP 8: Test Different Product**
1. **Go to Homepage**: Click logo or "Kembali ke Katalog"
2. **Click Different Product**: E.g., "Smartphone XZB 13 Pro"
3. **Click "Tambah ke Keranjang"**
4. **Expected**:
   - ✅ Success message for new product
   - ✅ Redirected to cart
   - ✅ Cart now shows 2 different products

### **STEP 9: Test Logout & Login Again**
1. **Logout**: Find logout button (usually in navbar or menu)
2. **Go to Product**: Click any product
3. **Check Button**: Should show **"Login untuk Membeli"** again ✅
4. **Login with Different User**: (if available)
5. **Go to Cart**: Different user should have empty/different cart

---

## ✅ TEST CHECKLIST

### **Basic Add to Cart**
- [ ] Logged in user can click "Tambah ke Keranjang"
- [ ] Success message appears
- [ ] Product added to cart
- [ ] Redirected to cart page

### **Authentication**
- [ ] Not logged in users see "Login untuk Membeli"
- [ ] Clicking login button goes to login page
- [ ] After login, button shows "Tambah ke Keranjang"
- [ ] Cart is user-specific (different for each user)

### **Quantity Management**
- [ ] First add creates CartItem with qty=1
- [ ] Second add increments qty to 2
- [ ] Third add increments qty to 3
- [ ] Each add shows correct qty in message

### **Multiple Products**
- [ ] Can add different products to same cart
- [ ] Each product shows separately
- [ ] Each product has own quantity
- [ ] Cart displays all products

### **Stock Status**
- [ ] Button disabled when product stock=0
- [ ] Button text shows "Stok Habis"
- [ ] Button text shows "Stok Terbatas (X)" when low stock
- [ ] Can't add more than available stock (validation error)

### **Messages**
- [ ] Success message shows product name
- [ ] Success message shows quantity added
- [ ] Success message is green/positive
- [ ] Warning messages appear for stock errors
- [ ] Warning messages are orange/yellow

### **Redirect**
- [ ] After add, redirects to cart page
- [ ] Redirect respects `next` parameter if provided
- [ ] Can navigate back to product (browser back button works)

### **Cart Page**
- [ ] All added products display correctly
- [ ] Product names show
- [ ] Quantities show correctly
- [ ] Prices show in Rp format
- [ ] Total price calculated correctly

---

## 🐛 QUICK TROUBLESHOOTING

### **Issue: "Login untuk Membeli" button not showing**
**Cause**: User is logged in  
**Solution**: Logout first, or check `{% if user.is_authenticated %}`

### **Issue: Clicking button does nothing**
**Cause 1**: Stock is 0 (button disabled)  
**Solution**: Check if button is grayed out; try different product

**Cause 2**: Not logged in  
**Solution**: Login first if button is "Login untuk Membeli"

**Cause 3**: URL not found  
**Solution**: Check browser console (F12) for 404 error

### **Issue: Product not appearing in cart**
**Cause**: Stock validation failed  
**Solution**: Check cart page for warning message; try smaller quantity

### **Issue: Wrong quantity showing**
**Cause**: Quantity not incremented properly  
**Solution**: Clear browser cache, try again

### **Issue: "Add to Cart" button gives error**
**Cause**: Product doesn't exist or is inactive  
**Solution**: Use seed data products

---

## 📝 EXPECTED RESULTS

### **Scenario 1: First Time User**
```
1. Browse homepage
2. Click product "Laptop Gaming Pro 15"
   → Shows product detail
   → Button shows "Login untuk Membeli" (user not logged in)
3. Click "Login untuk Membeli"
   → Redirected to login page
4. Login with username/password
   → Redirected back to product detail page
   → Button now shows "Tambah ke Keranjang"
5. Click "Tambah ke Keranjang"
   → Success message: "✅ 'Laptop Gaming Pro 15' berhasil ditambahkan..."
   → Redirected to /cart/
   → See product in cart with qty=1, price showing
```

### **Scenario 2: Existing Cart User**
```
1. Already logged in user
2. Click product detail page
   → Button shows "Tambah ke Keranjang" (user logged in)
3. Click button
   → Success message: "✅ 'Product' berhasil ditambahkan..."
   → Redirected to /cart/
   → New product added OR quantity incremented
4. Go back to product
5. Click button again
   → Same success message
   → Redirected to /cart/
   → Same product now shows qty+1
```

### **Scenario 3: Stock Validation**
```
1. Product with 5 stock
2. Try to add qty=10
3. Button click
   → Warning message: "⚠️ Stok hanya tersedia 5 unit..."
   → Redirected back to product page (not to cart)
   → Product NOT added
4. Try again with qty=3
   → Success message
   → Product added with qty=3
```

---

## 🔍 VERIFY IN BROWSER CONSOLE

Press **F12** to open Developer Tools, then check:

### **Check Network Requests**
1. Click "Tambah ke Keranjang"
2. Open Network tab
3. Should see POST or GET request to `/add-to-cart/...`
4. Response status: 302 (redirect) ✅

### **Check Console Messages**
1. Look for any JavaScript errors (red ❌)
2. Should see no errors
3. Should see redirect happening

### **Check Database (Optional)**
```bash
# In Django shell
python manage.py shell
>>> from master_products.models import Cart, CartItem
>>> Cart.objects.all()  # See all carts
>>> CartItem.objects.all()  # See all items in carts
```

---

## 🎯 SUCCESS CRITERIA

**All tests passed if**:
✅ Add to Cart button visible for logged-in users  
✅ "Login untuk Membeli" shown for non-logged-in users  
✅ Products successfully added to cart  
✅ Quantities increment properly  
✅ Stock validation prevents overselling  
✅ Success/warning messages display correctly  
✅ Cart page shows updated content  
✅ Multiple products can be added  
✅ Each user has separate cart  
✅ No console errors  

---

## 📊 TEST RESULTS TEMPLATE

After testing, fill this out:

```
╔═══════════════════════════════════════════════════════════════╗
║            ADD TO CART - TEST RESULTS                         ║
╠═══════════════════════════════════════════════════════════════╣
║ Tester: _____________________                                ║
║ Date: _____________________                                  ║
║ Status: [ ] PASS  [ ] FAIL  [ ] PARTIAL                      ║
╠═══════════════════════════════════════════════════════════════╣
║ TESTS PASSED:                                                 ║
║ [ ] Authentication check working                             ║
║ [ ] Add new product to cart                                  ║
║ [ ] Increment quantity on re-add                             ║
║ [ ] Stock validation working                                 ║
║ [ ] Multiple products in cart                                ║
║ [ ] Messages displaying correctly                            ║
║ [ ] Redirect to cart working                                 ║
║ [ ] Cart page showing content                                ║
║ [ ] Prices formatted correctly                               ║
║ [ ] No console errors                                        ║
╠═══════════════════════════════════════════════════════════════╣
║ ISSUES FOUND:                                                 ║
║ 1. _____________________________________                    ║
║ 2. _____________________________________                    ║
║ 3. _____________________________________                    ║
╠═══════════════════════════════════════════════════════════════╣
║ COMMENTS:                                                     ║
║ ________________________________________________________      ║
║ ________________________________________________________      ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📱 RESPONSIVE TESTING

### **Desktop (1920x1080)**
- [ ] Button clearly visible
- [ ] Button clickable
- [ ] No layout breaks
- [ ] Message displays fully

### **Tablet (768x1024)**
- [ ] Button still clickable
- [ ] Layout responsive
- [ ] Message visible
- [ ] No horizontal scrolling

### **Mobile (375x667)**
- [ ] Button full width (easy to tap)
- [ ] Touch-friendly (not too small)
- [ ] Message readable
- [ ] No layout issues

---

## 🎓 WHAT TO LOOK FOR

### **Good Signs** ✅
- Product successfully added
- Quantity increments
- Messages are clear
- Prices calculated correctly
- No errors in console
- Smooth user flow
- Mobile friendly
- Fast response

### **Bad Signs** ❌
- 404 or 500 errors
- Product doesn't appear in cart
- Wrong quantity shown
- Messages not displaying
- Stock validation not working
- Redirects broken
- Layout broken on mobile
- Slow response

---

## 🏁 READY TO TEST!

Everything is configured and ready. Start with **STEP 1** above and follow through all steps.

**Estimated Time**: 10-15 minutes for all tests

**Next**: After testing passes, the Add to Cart feature is production-ready! 🚀

---

**Status**: ✅ **READY FOR MANUAL TESTING**

---
