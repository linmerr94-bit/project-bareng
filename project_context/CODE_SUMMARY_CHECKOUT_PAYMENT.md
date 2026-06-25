# CODE SUMMARY - Checkout & Payment Implementation

## 1️⃣ VIEWS.PY - Imports Updated

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import uuid
from master_products.models import (
    Product, Category, VendorRequest, Cart, CartItem, 
    Order, OrderItem, Brand
)
from master_brands.models import BrandProfile

User = get_user_model()
```

---

## 2️⃣ VIEWS.PY - New Functions

### A. checkout_view() - FULL CODE

```python
@login_required(login_url='master_products:login')
def checkout_view(request):
    """
    Menampilkan halaman checkout dan memproses pembuatan order dari cart.
    """
    
    try:
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id')
    except Cart.DoesNotExist:
        messages.error(request, '❌ Keranjang Anda kosong! Silakan tambahkan produk terlebih dahulu.')
        return redirect('master_products:product_list')
    
    if not cart_items.exists():
        messages.error(request, '❌ Keranjang Anda kosong! Silakan tambahkan produk terlebih dahulu.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        total_price = 0
        total_items = 0
        
        for item in cart_items:
            item.subtotal = float(item.price) * item.qty
            total_price += item.subtotal
            total_items += item.qty
        
        context = {
            'cart_items': cart_items,
            'total_items': total_items,
            'total_price': total_price,
            'total_price_formatted': f"Rp{total_price:,.0f}",
            'payment_methods': Order.PAYMENT_METHOD_CHOICES,
        }
        
        return render(request, 'master_products/checkout.html', context)
    
    if request.method == 'POST':
        receiver_name = request.POST.get('receiver_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        payment_method = request.POST.get('payment_method', '').strip()
        
        if not all([receiver_name, phone, shipping_address, payment_method]):
            messages.error(request, '❌ Semua field harus diisi!')
            return redirect('master_products:checkout')
        
        if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
            messages.error(request, '❌ Metode pembayaran tidak valid!')
            return redirect('master_products:checkout')
        
        try:
            with transaction.atomic():
                cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id')
                
                if not cart_items.exists():
                    messages.error(request, '❌ Keranjang Anda kosong!')
                    return redirect('master_products:product_list')
                
                # Validasi stok
                stock_errors = []
                for item in cart_items:
                    if item.product_id.stock < item.qty:
                        stock_errors.append(
                            f"'{item.product_id.product_name}': hanya tersedia {item.product_id.stock} unit, "
                            f"Anda memesan {item.qty} unit"
                        )
                
                if stock_errors:
                    error_msg = '⚠️ Stok produk tidak mencukupi:\n• ' + '\n• '.join(stock_errors)
                    messages.warning(request, error_msg)
                    return redirect('master_products:view_cart')
                
                # Hitung total
                total_amount = sum(float(item.price) * item.qty for item in cart_items)
                
                # Get brand dari cart items
                first_brand = cart_items.first().product_id.brand_id
                
                # Generate order code
                order_code = f"ORD-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
                
                # Create order
                order = Order.objects.create(
                    user_id=request.user,
                    brand_id=first_brand,
                    order_code=order_code,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    receiver_name=receiver_name,
                    phone=phone,
                    status='pending',
                    payment_status='pending'
                )
                
                # Create order items & decrement stock
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order_id=order,
                        product_id=cart_item.product_id,
                        price=cart_item.price,
                        qty=cart_item.qty
                    )
                    
                    product = cart_item.product_id
                    product.stock -= cart_item.qty
                    product.save()
                
                # Delete cart items
                cart_items.delete()
                
                messages.success(
                    request,
                    f'✅ Order berhasil dibuat! Kode Order: <strong>{order_code}</strong><br>'
                    f'Total pembayaran: <strong>Rp{total_amount:,.0f}</strong><br>'
                    f'Silakan lanjutkan ke halaman pembayaran.'
                )
                
                return redirect('master_products:process_payment', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat membuat order: {str(e)}')
            return redirect('master_products:checkout')
```

### B. process_payment_view() - FULL CODE

```python
@login_required(login_url='master_products:login')
def process_payment_view(request, order_id):
    """
    Menampilkan halaman pembayaran dan memproses simulasi pembayaran.
    """
    
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
        
        context = {
            'order': order,
            'order_items': order_items,
            'order_code': order.order_code,
            'total_amount': order.total_amount,
            'total_amount_formatted': f"Rp{order.total_amount:,.0f}",
            'payment_method_display': dict(Order.PAYMENT_METHOD_CHOICES)[order.payment_method],
            'receiver_name': order.receiver_name,
            'shipping_address': order.shipping_address,
            'phone': order.phone,
        }
        
        return render(request, 'master_products/payment.html', context)
    
    if request.method == 'POST':
        try:
            order.status = 'confirmed'
            order.payment_status = 'paid'
            order.save()
            
            messages.success(
                request,
                f'✅ Pembayaran berhasil diproses!<br>'
                f'Order Code: <strong>{order.order_code}</strong><br>'
                f'Status: <strong>Menunggu Konfirmasi Penjual</strong><br>'
                f'Anda akan menerima notifikasi via email.'
            )
            
            return redirect('master_products:order_confirmation', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat memproses pembayaran: {str(e)}')
            return redirect('master_products:process_payment', order_id=order.order_id)
```

### C. order_confirmation_view() - FULL CODE

```python
@login_required(login_url='master_products:login')
def order_confirmation_view(request, order_id):
    """
    Menampilkan halaman konfirmasi order setelah pembayaran sukses.
    """
    
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
    
    context = {
        'order': order,
        'order_items': order_items,
        'order_code': order.order_code,
        'total_amount': order.total_amount,
        'total_amount_formatted': f"Rp{order.total_amount:,.0f}",
        'payment_method_display': dict(Order.PAYMENT_METHOD_CHOICES)[order.payment_method],
        'status_display': dict(Order.ORDER_STATUS_CHOICES)[order.status],
        'payment_status_display': dict(Order.PAYMENT_STATUS_CHOICES)[order.payment_status],
        'receiver_name': order.receiver_name,
        'shipping_address': order.shipping_address,
        'phone': order.phone,
        'order_date': order.order_date,
    }
    
    return render(request, 'master_products/order_confirmation.html', context)
```

### D. order_list_view() - FULL CODE

```python
@login_required(login_url='master_products:login')
def order_list_view(request):
    """
    Menampilkan halaman list semua order milik customer yang login.
    """
    
    orders = Order.objects.filter(
        user_id=request.user
    ).select_related('brand_id').order_by('-order_date')
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
    }
    
    return render(request, 'master_products/order_list.html', context)
```

### E. order_detail_view() - FULL CODE

```python
@login_required(login_url='master_products:login')
def order_detail_view(request, order_id):
    """
    Menampilkan halaman detail order dengan OrderItem lengkap.
    """
    
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:order_list')
    
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:order_list')
    
    order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
    
    context = {
        'order': order,
        'order_items': order_items,
        'order_code': order.order_code,
        'total_amount': order.total_amount,
        'total_amount_formatted': f"Rp{order.total_amount:,.0f}",
        'payment_method_display': dict(Order.PAYMENT_METHOD_CHOICES)[order.payment_method],
        'status_display': dict(Order.ORDER_STATUS_CHOICES)[order.status],
        'payment_status_display': dict(Order.PAYMENT_STATUS_CHOICES)[order.payment_status],
        'receiver_name': order.receiver_name,
        'shipping_address': order.shipping_address,
        'phone': order.phone,
        'order_date': order.order_date,
        'brand': order.brand_id,
    }
    
    return render(request, 'master_products/order_detail.html', context)
```

---

## 3️⃣ URLS.PY - Complete Routes

```python
from django.urls import path
from . import views

app_name = 'master_products'

urlpatterns = [
    # ==================== CUSTOMER - PRODUCT CATALOG ====================
    path('', views.product_list, name='product_list'),
    path('api/search/', views.product_list_ajax, name='product_list_ajax'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # ==================== CUSTOMER - SHOPPING CART ====================
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    
    # ==================== CUSTOMER - CHECKOUT & PAYMENT ====================
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment_view, name='process_payment'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # ==================== AUTHENTICATION ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_customer_view, name='register_customer'),
    path('register-vendor/', views.register_vendor_view, name='register_vendor'),
    
    # ==================== VENDOR - DASHBOARD & PRODUCT MANAGEMENT ====================
    path('vendor/dashboard/', views.vendor_dashboard_view, name='vendor_dashboard'),
    path('vendor/add-product/', views.add_product_view, name='add_product'),
]
```

---

## 4️⃣ Cart.html - Updated Button

**OLD CODE:**
```html
<button class="btn-checkout w-full" onclick="alert('✅ Fitur checkout akan segera hadir!')">
    <i class="fas fa-credit-card"></i>
    Lanjut ke Pembayaran
</button>
```

**NEW CODE:**
```html
<a href="{% url 'master_products:checkout' %}" class="btn-checkout w-full text-center" style="display: flex; justify-content: center;">
    <i class="fas fa-credit-card"></i>
    Lanjut ke Pembayaran
</a>
```

---

## 5️⃣ Key Features

### Atomic Transaction
```python
with transaction.atomic():
    # Jika ada error, semua operasi rollback
    # Cegah data corruption
```

### Stock Validation
```python
# Double-check sebelum create order
if item.product_id.stock < item.qty:
    # Show error & redirect
```

### Permission Check
```python
if order.user_id != request.user:
    # Akses ditolak
```

### Order Code Generation
```python
order_code = f"ORD-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
# Contoh: ORD-1719000000-ABC123
```

---

## 6️⃣ Database Schema

### Order Model (existing, used as-is)
```python
class Order(models.Model):
    order_id = AutoField(primary_key=True)
    user_id = ForeignKey(User)
    brand_id = ForeignKey(Brand)
    order_code = CharField(unique=True)
    status = CharField(choices=[pending, confirmed, processing, shipped, delivered, cancelled, returned])
    payment_status = CharField(choices=[pending, paid, failed, refunded])
    total_amount = DecimalField
    # ... more fields
```

### OrderItem Model (existing, used as-is)
```python
class OrderItem(models.Model):
    order_item_id = AutoField(primary_key=True)
    order_id = ForeignKey(Order)
    product_id = ForeignKey(Product)
    price = DecimalField  # Snapshot saat order dibuat
    qty = IntegerField
```

---

## ✨ Summary

**Total Code Lines Added**: ~450 (views) + ~1500 (templates)
**Database Changes**: None (models already existed)
**External Dependencies**: None (Django built-ins only)
**Ready for Production**: ⚠️ Belum (perlu payment gateway & email)
**Ready for MVP Demo**: ✅ YES!

