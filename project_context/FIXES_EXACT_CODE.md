# ✅ EXACT CODE FIXES FOR CRITICAL ISSUES

## Fix #1: Add F() Import to views.py

**File:** `master_products/views.py`  
**Line 9:** 

### CURRENT (BROKEN):
```python
from django.db import transaction, models
```

### FIXED:
```python
from django.db import transaction, models
from django.db.models import F  # ADD THIS LINE
```

---

## Fix #2: Remove Duplicate @login_required Decorator

**File:** `master_products/views.py`  
**Lines 1147-1150:**

### CURRENT (BROKEN):
```python
@login_required(login_url='master_products:login')
@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def checkout_view(request):
```

### FIXED:
```python
@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def checkout_view(request):
```

---

## Fix #3: Add rating Field to Product Model

**File:** `master_products/models.py`  
**After Line 256 (after stock field, before image field):**

### ADD THIS NEW FIELD:
```python
    # Rating dari reviews yang diberikan customer
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        db_column='rating',
        help_text="Rating rata-rata produk dari customer reviews (0.0-5.0)"
    )
    
    # Jumlah reviews
    review_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        db_column='review_count',
        help_text="Jumlah customer yang telah memberikan review"
    )
```

### THEN RUN MIGRATIONS:
```bash
python manage.py makemigrations master_products
python manage.py migrate
```

---

## Fix #4: Replace All `product_image` with `image` in Templates

### Template 1: cart.html

**Lines 432-433:**

#### CURRENT (BROKEN):
```html
                            {% if item.product_id.product_image %}
                                <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}" onerror="this.onerror=null; this.src='https://via.placeholder.com/120x120?text=No+Image';">
```

#### FIXED:
```html
                            {% if item.product_id.image %}
                                <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}" onerror="this.onerror=null; this.src='https://via.placeholder.com/120x120?text=No+Image';">
```

---

### Template 2: checkout.html

**Lines 625-627:**

#### CURRENT (BROKEN):
```html
                                                {% if item.product_id.product_image %}
                                                        <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}">
```

#### FIXED:
```html
                                                {% if item.product_id.image %}
                                                        <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}">
```

---

### Template 3: checkout_detailed.html

**Lines 621-623:**

#### CURRENT (BROKEN):
```html
                                    {% if item.product_id.product_image %}
                                            <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}">
```

#### FIXED:
```html
                                    {% if item.product_id.image %}
                                            <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}">
```

---

### Template 4: payment_gateway.html

**Lines 543-545:**

#### CURRENT (BROKEN):
```html
                                {% if item.product_id.product_image %}
                                        <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}">
```

#### FIXED:
```html
                                {% if item.product_id.image %}
                                        <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}">
```

---

### Template 5: payment_confirmation.html

**Lines 280-282:**

#### CURRENT (BROKEN):
```html
                                {% if item.product_id.product_image %}
                                        <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}">
```

#### FIXED:
```html
                                {% if item.product_id.image %}
                                        <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}">
```

---

### Template 6: order_detail.html

**Lines 336-338:**

#### CURRENT (BROKEN):
```html
                                {% if item.product_id.product_image %}
                                        <img src="{{ item.product_id.product_image.url }}" alt="{{ item.product_id.product_name }}">
```

#### FIXED:
```html
                                {% if item.product_id.image %}
                                        <img src="{{ item.product_id.image.url }}" alt="{{ item.product_id.product_name }}">
```

---

## Fix #5: Add Missing Cart Update/Remove Views

**File:** `master_products/views.py`  
**Add at the end (before the last admin views section around line 2050):**

```python
@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def update_cart_item(request):
    """
    AJAX endpoint untuk update quantity produk di cart.
    
    POST JSON Parameters:
    - item_id: CartItem ID
    - quantity: Jumlah baru (minimum 1)
    
    Response: JSON dengan status success/error
    """
    import json
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity', 1)
        
        # Validasi quantity
        if new_quantity < 1:
            new_quantity = 1
        if new_quantity > 999:
            new_quantity = 999
        
        # Get CartItem
        try:
            cart_item = CartItem.objects.get(cart_item_id=item_id, cart_id__user_id=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item tidak ditemukan'}, status=404)
        
        # Validasi stok
        product = cart_item.product_id
        if product.stock < new_quantity:
            return JsonResponse({
                'status': 'error', 
                'message': f'Stok hanya tersedia {product.stock} unit'
            }, status=400)
        
        # Update quantity
        cart_item.qty = new_quantity
        cart_item.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Quantity diperbarui menjadi {new_quantity}',
            'new_quantity': new_quantity
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """
    AJAX endpoint untuk menghapus item dari cart.
    
    URL Parameters:
    - item_id: CartItem ID yang akan dihapus
    
    Response: JSON dengan status success/error
    """
    try:
        # Get CartItem
        try:
            cart_item = CartItem.objects.get(cart_item_id=item_id, cart_id__user_id=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item tidak ditemukan'}, status=404)
        
        # Delete item
        product_name = cart_item.product_id.product_name
        cart_item.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'"{product_name}" dihapus dari keranjang'
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
```

**Don't forget JsonResponse import at top of views.py!**

Add to line 1:
```python
from django.http import JsonResponse
```

---

## Fix #6: Add Missing URL Patterns

**File:** `master_products/urls.py`  
**Add these lines after the `path('cart/', ...)` line (around line 22):**

```python
    # ==================== CUSTOMER - SHOPPING CART (AJAX) ====================
    path('api/update-cart/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
```

---

## Fix #7: Update cart.html JavaScript to Use Correct Endpoints

**File:** `master_products/templates/master_products/cart.html`  
**Lines 523-547 (updateQty function) - REPLACE ENTIRE FUNCTION:**

### CURRENT (BROKEN):
```javascript
        function updateQty(itemId, change) {
            // Get current quantity
            const input = event.target.parentElement.querySelector('.qty-display');
            const currentQty = parseInt(input.value);
            const newQty = Math.max(1, currentQty + change);
            
            // Update cart via AJAX
            fetch(`/update_cart/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quantity: newQty
                })
            })
            .then(response => response.json())
            .then(data => {
                location.reload();
            })
            .catch(error => console.error('Error:', error));
        }
```

### FIXED:
```javascript
        function updateQty(itemId, change) {
            // Get current quantity
            const input = event.target.parentElement.querySelector('.qty-display');
            const currentQty = parseInt(input.value);
            const newQty = Math.max(1, currentQty + change);
            
            // Update cart via AJAX
            fetch(`{% url 'master_products:update_cart_item' %}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quantity: newQty
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    input.value = newQty;
                    // Recalculate totals without full page reload
                    recalculateCart();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        }
```

---

## Fix #8: Update cart.html removeItem Function

**File:** `master_products/templates/master_products/cart.html`  
**Lines 549-563 (removeItem function) - REPLACE ENTIRE FUNCTION:**

### CURRENT (BROKEN):
```javascript
        function removeItem(itemId) {
            if (confirm('Hapus item dari keranjang?')) {
                fetch(`/remove_from_cart/${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    location.reload();
                })
                .catch(error => console.error('Error:', error));
            }
        }
```

### FIXED:
```javascript
        function removeItem(itemId) {
            if (confirm('Hapus item dari keranjang?')) {
                fetch(`{% url 'master_products:remove_from_cart' item_id=0 %}`.replace('0', itemId), {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
```

---

## Fix #9: Remove product_detail_simplified.html Rating References (Optional)

If Product doesn't have a rating aggregation, either:

**Option A: Remove rating section entirely from product_detail_simplified.html (Lines 252-267)**

**Option B: Populate rating dynamically from Review model**

Add to view context (product_detail_by_id view around line 388):
```python
# Calculate average rating from reviews
avg_rating_data = product.reviews.aggregate(avg_rating=Avg('rating'))
average_rating = avg_rating_data['avg_rating'] or 0
context['average_rating'] = average_rating
```

---

## VERIFICATION CHECKLIST AFTER FIXES

```
✅ Step 1: Run migrations
   python manage.py makemigrations master_products
   python manage.py migrate

✅ Step 2: Run Django check
   python manage.py check

✅ Step 3: Test product sorting (should not crash on rating sort)
   - Visit product list
   - Try sort by "Rating"
   
✅ Step 4: Test cart operations
   - Add product to cart
   - Go to cart page (images should display)
   - Click "Update Qty" button
   - Click "Remove" button
   
✅ Step 5: Test checkout flow
   - Go through checkout (images should display)
   - Make payment
   - View invoice (images should display)

✅ Step 6: Monitor browser console
   - Should have NO 404 errors
   - Should have NO AttributeError messages
```

---

## PRIORITY ORDER TO FIX

1. **FIRST:** Fix #1 - Add F() import (5 seconds)
2. **SECOND:** Fix #5 - Add cart views (2 minutes)
3. **THIRD:** Fix #6 - Add URL patterns (1 minute)
4. **FOURTH:** Fix #3 - Add rating fields + migrate (3 minutes)
5. **FIFTH:** Fix #2 - Remove duplicate decorator (10 seconds)
6. **SIXTH:** Fix #4 - Update 6 templates (5 minutes)
7. **SEVENTH:** Fix #7 + #8 - Update JavaScript (2 minutes)
8. **FINAL:** Run migrations and verify all tests pass

**Total Time:** ~15 minutes

---

## EMERGENCY CONTACT POINTS
If any fix fails during implementation:
- Check Django syntax in views (Python indentation)
- Verify URLs use `path()` from django.urls
- Ensure template variable names match exactly (case-sensitive)
- Run `python manage.py check` after each major change
