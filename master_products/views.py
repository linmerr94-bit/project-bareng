from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q, Count, F, Avg, Sum
from django.urls import reverse
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from datetime import datetime
import json
import uuid
import random
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings as django_settings
from master_products.models import (
    Product, Category, VendorRequest, Cart, CartItem, 
    Order, OrderItem, Brand, Review,
    UserTwoFactor, LoginSession, EmailOTP
)
from master_products.decorators import seller_required, customer_required

# Import custom User model
User = get_user_model()


# ============================================================================
# AUTHENTICATION & ROLE-BASED VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
def dashboard_redirect_view(request):
    """
    View untuk redirect user ke dashboard sesuai dengan role mereka.
    
    Redirect Logic:
    - Admin → Platform Admin Dashboard (/platform-admin/dashboard/)
    - Brand (Approved) → Seller Dashboard (/toko/dashboard/)
    - Brand (Pending/Other) → Product List + Warning Message
    - Customer → Product List (/)
    
    Digunakan sebagai LOGIN_REDIRECT_URL untuk auto-redirect setelah login.
    """
    user = request.user
    
    # ==================== ADMIN ====================
    if user.role == 'admin' and user.is_staff:
        return redirect('master_products:admin_platform_dashboard')
    
    # ==================== BRAND (SELLER) ====================
    elif user.role == 'brand':
        current_toko = getattr(user, 'toko', None)
        if current_toko is None:
            messages.error(request, '❌ Profil toko Anda belum terdaftar!')
            return redirect('master_products:product_list')

        if current_toko.status != 'approved':
            messages.warning(
                request,
                f'⏳ Toko Anda masih menunggu persetujuan dari admin. Status: {current_toko.get_status_display()}'
            )
            return redirect('master_products:product_list')

        return redirect('master_products:seller_dashboard')
    
    # ==================== CUSTOMER ====================
    else:  # customer atau default
        return redirect('master_products:product_list')


@login_required(login_url='master_products:login')
@seller_required
def seller_dashboard(request):
    """
    Dashboard untuk penjual (brand/vendor) VOLTA.
    
    Menampilkan:
    1. Total produk yang dijual penjual ini
    2. Total pesanan masuk (orders)
    3. Tabel daftar produk dengan ringkasan
    4. Tabel pesanan terbaru
    
    Hanya bisa diakses oleh user dengan role 'brand'.
    """
    
    # ==================== GET STORE PROFILE (TOKO) ====================
    current_toko = getattr(request.user, 'toko', None)
    if current_toko is None:
        messages.error(request, '❌ Profil toko Anda belum terdaftar!')
        return redirect('master_products:product_list')

    if current_toko.status != 'approved':
        messages.warning(
            request,
            f'⏳ Toko Anda masih dalam proses persetujuan. Status: {current_toko.get_status_display()}'
        )
        return redirect('master_products:product_list')
    
    # ==================== GET TOKO PRODUCTS ====================
    products = Product.objects.filter(
        brand_id=current_toko,
        is_active=True
    ).order_by('-created_at')
    
    total_products = products.count()
    
    # ==================== GET SELLER ORDERS ====================
    orders = Order.objects.filter(
        brand_id=current_toko
    ).select_related('user_id').order_by('-created_at')
    
    total_orders = orders.count()
    
    # Get last 5 orders for recent table
    recent_orders = orders[:5]
    
    # ==================== BUILD CONTEXT ====================
    context = {
        'toko': current_toko,
        'seller_brand': current_toko,
        'total_products': total_products,
        'total_orders': total_orders,
        'products': products[:10],  # Top 10 produk untuk tabel
        'recent_orders': recent_orders,
    }
    
    return render(request, 'master_products/seller_dashboard.html', context)


def product_list(request):
    """
    Menampilkan halaman katalog produk VOLTA.
    
    Fitur:
    1. Pencarian produk (search bar) - filter by nama atau deskripsi
    2. Filter kategori (pill buttons) - dinamis berdasarkan kategori pilihan
    3. Sorting - Terbaru, Harga (terendah/tertinggi), Rating
    
    Query Parameters:
    - q: search query (nama/deskripsi produk)
    - category: category ID untuk filter
    - sort: terbaru|harga_terendah|harga_tertinggi|rating
    """
    
    # ==================== 1. QUERY BASE - Produk aktif dari brand approved ====================
    products = Product.objects.filter(
        is_active=True,
        brand_id__status='approved'
    ).select_related('brand_id', 'category_id')
    
    # ==================== 2. FITUR PENCARIAN (SEARCH BAR) ====================
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Filter produk berdasarkan nama, deskripsi, atau brand (case-insensitive)
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand_id__brand_name__icontains=search_query)
        )
    
    # ==================== 3. FITUR FILTER KATEGORI ====================
    # Ambil semua kategori untuk dropdown/pills di HTML
    categories = Category.objects.all().order_by('category_name')
    
    # Filter kategori jika ada parameter dari pill buttons
    selected_category = request.GET.get('category', '')
    selected_category_name = None
    if selected_category:
        try:
            selected_category = int(selected_category)
            products = products.filter(category_id=selected_category)
            selected_category_name = Category.objects.get(category_id=selected_category).category_name
        except (ValueError, Category.DoesNotExist):
            selected_category = None
    else:
        selected_category = None
    
    # ==================== 4. FITUR SORTING ====================
    sort_param = request.GET.get('sort', 'terbaru').lower()
    if sort_param == 'harga_terendah':
        products = products.order_by('price')
    elif sort_param == 'harga_tertinggi':
        products = products.order_by('-price')
    elif sort_param == 'rating':
        products = products.order_by('-rating')
    else:  # default: 'terbaru'
        products = products.order_by('-created_at')
    
    # ==================== 5. HITUNG CART COUNT ====================
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user_id=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    
    # ==================== 6. BUILD CONTEXT ====================
    context = {
        # Data produk
        'products': products,
        'total_products': products.count(),
        
        # Kategori & filtering
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_name': selected_category_name,
        
        # Search & sorting
        'search_query': search_query,
        'sort_param': sort_param,
        
        # Cart count
        'cart_count': cart_count,
    }
    
    return render(request, 'master_products/product_list.html', context)


def product_list_ajax(request):
    """
    AJAX Endpoint untuk real-time search & filter produk.
    Mengembalikan hanya HTML dari product_list_content.html tanpa wrapper.
    
    Query Parameters:
    - q: search query (nama/deskripsi produk)
    - category: category ID untuk filter
    - sort: terbaru|harga_terendah|harga_tertinggi|rating
    """
    
    # ==================== 1. QUERY BASE ====================
    products = Product.objects.filter(
        is_active=True,
        brand_id__status='approved'
    ).select_related('brand_id', 'category_id')
    
    # ==================== 2. PENCARIAN ====================
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand_id__brand_name__icontains=search_query)
        )
    
    # ==================== 3. FILTER KATEGORI ====================
    categories = Category.objects.all().order_by('category_name')
    
    selected_category = request.GET.get('category', '')
    selected_category_name = None
    if selected_category:
        try:
            selected_category = int(selected_category)
            products = products.filter(category_id=selected_category)
            selected_category_name = Category.objects.get(category_id=selected_category).category_name
        except (ValueError, Category.DoesNotExist):
            selected_category = None
    else:
        selected_category = None
    
    # ==================== 4. SORTING ====================
    sort_param = request.GET.get('sort', 'terbaru').lower()
    if sort_param == 'harga_terendah':
        products = products.order_by('price')
    elif sort_param == 'harga_tertinggi':
        products = products.order_by('-price')
    elif sort_param == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')
    
    # ==================== 5. BUILD CONTEXT ====================
    context = {
        'products': products,
        'total_products': products.count(),
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_name': selected_category_name,
        'search_query': search_query,
        'sort_param': sort_param,
    }
    
    # Return hanya HTML dari product_list_content.html (tanpa wrapper)
    return render(request, 'master_products/includes/product_list_content.html', context)


def product_detail(request, slug):
    """
    Menampilkan halaman detail produk individual berdasarkan slug.
    
    URL Parameters:
    - slug: URL-friendly slug identifier dari produk yang ingin ditampilkan
    
    Fitur:
    1. Tampilkan detail produk lengkap dengan gambar, nama, harga
    2. Tampilkan informasi brand/vendor yang menjual produk
    3. Tampilkan kategori, stok, dan deskripsi lengkap
    4. Tampilkan status stok (Tersedia / Terbatas / Habis)
    5. Tombol "Tambah ke Keranjang" untuk customer yang sudah login
    """
    
    # ==================== 1. AMBIL PRODUK DARI DATABASE ====================
    product = get_object_or_404(
        Product.objects.select_related('brand_id', 'category_id').filter(
            is_active=True,
            brand_id__status='approved'
        ),
        slug=slug
    )
    
    # ==================== 2. DETEKSI STATUS STOK ====================
    stock_status = 'Stok Tersedia'
    stock_color = 'text-green-600'
    stock_badge_bg = 'bg-green-500/20'
    
    if product.stock <= 0:
        stock_status = 'Stok Habis'
        stock_color = 'text-red-600'
        stock_badge_bg = 'bg-red-500/20'
    elif product.stock < 10:
        stock_status = f'Stok Terbatas ({product.stock} unit)'
        stock_color = 'text-orange-600'
        stock_badge_bg = 'bg-orange-500/20'
    
    # ==================== 3. BUILD CONTEXT ====================
    context = {
        # Data produk
        'product': product,
        'brand': product.brand_id,
        'category': product.category_id,
        
        # Harga
        'price': product.price,
        'price_formatted': f"Rp{product.price:,.0f}",
        
        # Stock information
        'stock_status': stock_status,
        'stock_color': stock_color,
        'stock_badge_bg': stock_badge_bg,
        'stock_quantity': product.stock,
    }
    
    return render(request, 'master_products/product_detail.html', context)


def product_detail_by_id(request, product_id):
    """
    Menampilkan halaman detail produk berdasarkan product_id (wrapper untuk product_detail).
    Redirect ke product_detail view dengan slug untuk konsistensi.
    """
    product = get_object_or_404(
        Product.objects.filter(is_active=True, brand_id__status='approved'),
        product_id=product_id
    )
    # Ambil reviews untuk produk ini
    reviews = product.reviews.all().select_related('user_id').order_by('-created_at')
    
    # Deteksi status stok
    stock_status = 'Stok Tersedia'
    stock_color = 'text-green-600'
    stock_badge_bg = 'bg-green-500/20'
    
    if product.stock <= 0:
        stock_status = 'Stok Habis'
        stock_color = 'text-red-600'
        stock_badge_bg = 'bg-red-500/20'
    elif product.stock < 10:
        stock_status = f'Stok Terbatas ({product.stock} unit)'
        stock_color = 'text-orange-600'
        stock_badge_bg = 'bg-orange-500/20'
    
    # Hitung average rating
    avg_rating_data = product.reviews.aggregate(avg_rating=Avg('rating'))
    average_rating = avg_rating_data['avg_rating'] or 0
    
    # Build context
    context = {
        'product': product,
        'brand': product.brand_id,
        'category': product.category_id,
        'price': product.price,
        'price_formatted': f"Rp{product.price:,.0f}",
        'stock_status': stock_status,
        'stock_color': stock_color,
        'stock_badge_bg': stock_badge_bg,
        'stock_quantity': product.stock,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    
    return render(request, 'master_products/product_detail.html', context)


def store_detail(request, brand_id):
    """
    Menampilkan halaman detail toko dengan profile dan semua produk dari toko tersebut.
    
    URL Parameters:
    - brand_id: Brand ID dari toko yang ingin ditampilkan
    
    Fitur:
    1. Tampilkan profil toko (nama, lokasi, deskripsi, badge terverifikasi)
    2. Tampilkan hero banner dengan informasi toko
    3. Tampilkan grid produk yang dijual toko ini
    4. Fitur search & filter pada produk toko
    5. Validasi toko hanya muncul jika sudah approved
    """
    
    # ==================== 1. AMBIL TOKO (BRAND) ====================
    brand = get_object_or_404(
        Brand.objects.prefetch_related('products'),
        brand_id=brand_id,
        status='approved'
    )
    
    # ==================== 2. AMBIL PRODUK DARI TOKO INI ====================
    products = Product.objects.filter(
        brand_id=brand,
        is_active=True
    ).select_related('category_id').order_by('-created_at')
    
    # ==================== 3. FITUR PENCARIAN (SEARCH BAR) ====================
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # ==================== 4. FITUR FILTER KATEGORI ====================
    categories = Category.objects.all().order_by('category_name')
    
    selected_category = request.GET.get('category', '')
    selected_category_name = None
    if selected_category:
        try:
            selected_category = int(selected_category)
            products = products.filter(category_id=selected_category)
            selected_category_name = Category.objects.get(category_id=selected_category).category_name
        except (ValueError, Category.DoesNotExist):
            selected_category = None
    else:
        selected_category = None
    
    # ==================== 5. FITUR SORTING ====================
    sort_param = request.GET.get('sort', 'terbaru').lower()
    if sort_param == 'harga_terendah':
        products = products.order_by('price')
    elif sort_param == 'harga_tertinggi':
        products = products.order_by('-price')
    elif sort_param == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')
    
    # ==================== 6. HITUNG CART COUNT ====================
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user_id=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    
    # ==================== 7. BUILD CONTEXT ====================
    context = {
        # Store info
        'brand': brand,
        'store_name': brand.brand_name,
        'store_location': 'Purwokerto',
        'store_description': brand.description if hasattr(brand, 'description') else 'Mitra toko VOLTA terpercaya',
        'is_verified': True,
        
        # Products
        'products': products,
        'total_products': products.count(),
        
        # Categories & filtering
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_name': selected_category_name,
        
        # Search & sorting
        'search_query': search_query,
        'sort_param': sort_param,
        
        # Cart count
        'cart_count': cart_count,
    }
    
    return render(request, 'master_products/store_detail.html', context)


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """
    Menambahkan produk ke keranjang belanja user via POST request.
    
    URL Parameters:
    - product_id: ID dari produk yang ingin ditambahkan ke keranjang
    
    POST Parameters:
    - quantity: Jumlah produk yang ingin ditambahkan (default: 1, optional)
    - next: URL untuk redirect setelah berhasil ditambahkan (optional)
    
    Fitur:
    1. Validasi login user (@login_required)
    2. Validasi method request harus POST
    3. Validasi produk ada dan aktif
    4. Validasi stok produk sebelum ditambahkan
    5. Jika produk sudah ada di keranjang, naikkan qty-nya (quantity + existing)
    6. Simpan harga produk pada saat ditambahkan ke cart (untuk historical tracking)
    7. Redirect ke halaman sebelumnya atau ke cart view
    """
    
    # ==================== 1. AMBIL PRODUK DARI DATABASE ====================
    product = get_object_or_404(
        Product.objects.select_related('brand_id').filter(
            is_active=True,
            brand_id__status='approved'
        ),
        product_id=product_id
    )
    
    # ==================== 2. AMBIL ATAU BUAT CART UNTUK USER ====================
    cart, created = Cart.objects.get_or_create(user_id=request.user)
    
    # ==================== 3. AMBIL & VALIDASI QUANTITY DARI POST ====================
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        if quantity > 999:  # Maksimal limit
            quantity = 999
    except (ValueError, TypeError):
        quantity = 1
    
    # ==================== 4. VALIDASI STOK PRODUK ====================
    if product.stock <= 0:
        messages.error(
            request,
            f'❌ Stok "{product.product_name}" sudah habis. Silakan coba produk lain.'
        )
        next_url = request.POST.get('next', f'/product/{product.slug}/')
        return redirect(next_url)
    
    if product.stock < quantity:
        messages.warning(
            request,
            f'⚠️ Stok "{product.product_name}" hanya tersedia {product.stock} unit. '
            f'Quantity yang diminta sudah disesuaikan ke {product.stock} unit.'
        )
        quantity = product.stock  # Sesuaikan dengan stok yang tersedia
    
    # ==================== 5. CEK APAKAH PRODUK SUDAH ADA DI KERANJANG ====================
    cart_item, item_created = CartItem.objects.get_or_create(
        cart_id=cart,
        product_id=product,
        defaults={
            'qty': quantity,
            'price': product.price  # Simpan harga pada saat ditambahkan
        }
    )
    
    # ==================== 6. JIKA SUDAH ADA, NAIKKAN QTY-NYA ====================
    if not item_created:
        new_quantity = cart_item.qty + quantity
        
        # Double-check stok untuk total quantity
        if product.stock < new_quantity:
            messages.warning(
                request,
                f'⚠️ Total pesanan "{product.product_name}" melebihi stok. '
                f'Stok tersedia: {product.stock} unit. Quantity dimulai dari {cart_item.qty}.'
            )
            next_url = request.POST.get('next', '/cart/')
            return redirect(next_url)
        
        # Update qty dan harga terbaru
        cart_item.qty = new_quantity
        cart_item.price = product.price  # Update harga ke harga terbaru
        cart_item.save()
    
    # ==================== 7. SUCCESS MESSAGE ====================
    messages.success(
        request,
        f'✅ "{product.product_name}" berhasil ditambahkan ke keranjang! '
        f'(Qty: {quantity} | Total: {cart_item.qty if not item_created else quantity})'
    )
    
    # ==================== 8. REDIRECT KE HALAMAN BERIKUTNYA ====================
    next_url = request.POST.get('next', '/cart/')
    return redirect(next_url)


@login_required(login_url='master_products:login')
def view_cart(request):
    """
    Menampilkan halaman keranjang belanja dengan detail produk dan total harga.
    
    Fitur:
    1. Tampilkan semua item dalam keranjang user yang login
    2. Hitung total harga: qty × price (harga saat ditambahkan) untuk setiap item
    3. Tampilkan informasi produk dan brand
    4. Opsi untuk update quantity atau remove item (via future AJAX)
    """
    
    # ==================== 1. AMBIL ATAU BUAT CART UNTUK USER ====================
    try:
        cart = Cart.objects.get(user_id=request.user)
    except Cart.DoesNotExist:
        # Jika user belum punya cart, buat yang baru
        cart = Cart.objects.create(user_id=request.user)
    
    # ==================== 2. AMBIL SEMUA ITEMS DI CART ====================
    # Optimize dengan select_related untuk brand dan product info
    cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id', 'product_id__category_id')
    
    # ==================== 3. HITUNG TOTAL CART ====================
    total_price = 0
    total_items = 0
    
    for item in cart_items:
        # Gunakan harga yang disimpan saat item ditambahkan ke cart
        item.subtotal = float(item.price) * item.qty
        total_price += item.subtotal
        total_items += item.qty
    
    # ==================== 4. BUILD CONTEXT ====================
    context = {
        # Cart data
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        
        # Pricing (calculated: qty × stored_price)
        'total_price': total_price,
        'total_price_formatted': f"Rp{total_price:,.0f}",
    }
    
    return render(request, 'master_products/cart.html', context)


def login_view(request):
    """
    Menampilkan halaman login VOLTA dan memproses autentikasi user.
    
    Logic:
    1. GET request: Tampilkan form login
    2. POST request: Proses login dengan auto-detect role + smart redirect
       - Ambil username dan password
       - Validasi tidak kosong
       - Authenticate user
       - Jika sukses:
         * Role == 'admin' → redirect ke /admin/ (Django Admin)
         * Role == 'brand' → redirect ke /toko/dashboard/ (Penjual Dashboard)
         * Role == 'customer' → redirect ke / (Homepage)
       - Jika gagal: tampilkan error message
    """
    if request.method == 'GET':
        return render(request, 'master_products/login.html')
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM ====================
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # ==================== VALIDASI DATA ====================
        if not username or not password:
            messages.error(request, '❌ Username dan Password harus diisi!')
            return render(request, 'master_products/login.html')
        
        # ==================== AUTHENTICATE USER ====================
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # User berhasil diautentikasi
            if hasattr(user, 'two_factor') and user.two_factor.is_enabled:
                otp = str(random.randint(100000, 999999))
                EmailOTP.objects.create(user=user, otp_code=otp)
                subject = 'Kode Verifikasi VOLTA'
                text_content = f'Kode OTP Anda adalah: {otp}'
                html_content = f"""
<div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; background: #1a1a2e; border-radius: 16px; padding: 40px; color: #ffffff;">
    <div style="text-align: center; margin-bottom: 24px;">
        <h1 style="color: #60a5fa; font-size: 28px; margin: 0;">⚡ VOLTA</h1>
        <p style="color: #9ca3af; margin-top: 8px;">Keamanan Akun Anda</p>
    </div>
    <div style="background: #16213e; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
        <p style="color: #9ca3af; margin: 0 0 12px 0;">Kode OTP Anda:</p>
        <div style="font-size: 40px; font-weight: bold; letter-spacing: 12px; color: #60a5fa;">{otp}</div>
        <p style="color: #6b7280; font-size: 13px; margin-top: 12px;">Berlaku selama 5 menit</p>
    </div>
    <p style="color: #6b7280; font-size: 13px; text-align: center;">Jangan bagikan kode ini kepada siapapun. Tim VOLTA tidak pernah meminta kode OTP Anda.</p>
</div>
"""
                msg = EmailMultiAlternatives(subject, text_content, django_settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                request.session['pending_user_id'] = user.pk
                return redirect('master_products:verify_otp')

            auth_login(request, user)
            
            # ==================== DYNAMIC ROLE-BASED REDIRECT ====================
            
            # 1. ADMIN → Custom Platform Admin Dashboard (Supervision, Approvals, Monitoring)
            if user.role == 'admin':
                messages.success(request, f'✅ Selamat datang Admin {user.username}! Masuk ke platform admin.')
                return redirect('master_products:admin_platform_dashboard')
            
            # 2. PENJUAL (BRAND) → Seller Dashboard
            elif user.role == 'brand':
                current_toko = getattr(user, 'toko', None)
                if current_toko is None:
                    messages.error(request, '❌ Akun penjual Anda belum memiliki profil toko yang terdaftar.')
                    return redirect('master_products:product_list')

                if current_toko.status != 'approved':
                    messages.warning(
                        request,
                        f'⏳ Akun penjual Anda belum disetujui. Status toko: {current_toko.get_status_display()}'
                    )
                    return redirect('master_products:product_list')

                messages.success(request, f'✅ Selamat datang kembali, {current_toko.nama_toko}! Akses dashboard Anda.')
                return redirect('master_products:dashboard_redirect')
            
            # 3. CUSTOMER → Homepage / Product List
            else:
                messages.success(request, f'✅ Selamat datang, {user.username}! Jelajahi produk kami.')
                return redirect('master_products:product_list')
        
        else:
            # Autentikasi gagal
            messages.error(request, '❌ Username atau Password salah. Silakan coba lagi.')
            return render(request, 'master_products/login.html', {'username': username})


def logout_view(request):
    """
    Logout user dari sistem dan redirect kembali ke halaman login.
    
    Fitur:
    - Panggil logout() untuk menghapus session user
    - Tampilkan success message
    - Redirect ke halaman login
    """
    logout(request)
    messages.success(request, 'Anda telah berhasil keluar dari sistem.')
    return redirect('master_products:login')

def register_customer_view(request):
    if request.method == 'GET':
        return render(request, 'master_products/register_customer.html')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not all([name, email, password, confirm_password]):
            messages.error(request, 'Semua field harus diisi!')
            return render(request, 'master_products/register_customer.html', {'name': name, 'email': email})
        
        if password != confirm_password:
            messages.error(request, 'Password dan Konfirmasi Password tidak cocok!')
            return render(request, 'master_products/register_customer.html', {'name': name, 'email': email})
        
        if len(password) < 8:
            messages.error(request, 'Password minimal 8 karakter!')
            return render(request, 'master_products/register_customer.html', {'name': name, 'email': email})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email ini sudah terdaftar! Silakan gunakan email lain atau login.')
            return render(request, 'master_products/register_customer.html', {'name': name})
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Username/Email ini sudah terdaftar!')
            return render(request, 'master_products/register_customer.html', {'name': name})
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
            )
            messages.success(request, 'Akun berhasil dibuat! Silakan login dengan email dan password Anda.')
            return redirect('master_products:login')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return render(request, 'master_products/register_customer.html', {'name': name, 'email': email})


def register_vendor_view(request):
    """
    Menampilkan halaman pendaftaran mitra vendor (brand resmi, supplier, distributor).
    Memproses pengajuan dan menyimpan ke database dengan status 'Pending'.
    
    Logic:
    1. GET request: Tampilkan halaman form
    2. POST request: Validasi dan simpan data ke VendorRequest model
       - Ambil data: vendor_name, email, nib, category, address, description
       - Validasi field tidak kosong
       - Validasi email
       - Cek NIB belum pernah terdaftar
       - Simpan data ke VendorRequest dengan status Pending tanpa membuat User/auth
       - Redirect ke halaman utama setelah sukses
    """
    if request.method == 'GET':
        return render(request, 'master_products/register_vendor.html')
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM ====================
        vendor_name = request.POST.get('vendor_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        nib = request.POST.get('nib', '').strip()
        category = request.POST.get('category', '').strip()
        address = request.POST.get('address', '').strip()
        description = request.POST.get('description', '').strip()
        
        # ==================== VALIDASI DATA ====================
        if not all([vendor_name, email, nib, category, address, description]):
            messages.error(request, 'Semua field harus diisi! Pastikan Nama Brand, Email, NIB, Kategori, Alamat, dan Deskripsi sudah diisi lengkap.')
            return render(request, 'master_products/register_vendor.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Alamat email tidak valid. Mohon gunakan format email yang benar.')
            return render(request, 'master_products/register_vendor.html')
        
        # ==================== VALIDASI NIB UNIK ====================
        if VendorRequest.objects.filter(nib=nib).exists():
            messages.error(request, 'NIB/KTP ini sudah pernah mendaftar sebelumnya. Jika ini adalah kesalahan, silakan hubungi admin VOLTA.')
            return render(request, 'master_products/register_vendor.html')

        # ==================== VALIDASI EMAIL DUPLIKAT PENGAJUAN ====================
        if VendorRequest.objects.filter(email=email, status='Pending').exists():
            messages.error(request, 'Email ini sudah digunakan untuk pengajuan mitra yang sedang diproses. Silakan cek email Anda atau hubungi admin jika perlu bantuan.')
            return render(request, 'master_products/register_vendor.html')
        
        # ==================== SIMPAN KE DATABASE ====================
        try:
            vendor_request = VendorRequest.objects.create(
                user=None,
                vendor_name=vendor_name,
                email=email,
                nib=nib,
                category=category,
                address=address,
                description=description,
                status='Pending'
            )
            
            messages.success(
                request,
                'Pengajuan pendaftaran toko berhasil dikirim! Silakan tunggu kurasi admin VOLTA. Kami akan menghubungi Anda melalui email dalam 2-5 hari kerja.'
            )
            return redirect('master_products:product_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat memproses pengajuan: {str(e)}')
            return render(request, 'master_products/register_vendor.html')


@login_required(login_url='master_products:login')
@seller_required
def add_product_view(request):
    """
    Menampilkan form dan memproses penambahan produk elektronik baru.
    Penjual (Seller/Brand) dapat menambahkan produk ke katalog mereka.
    
    Keamanan:
    - @login_required: User harus sudah login
    - @seller_required: User harus penjual yang disetujui
    - Ownership check: Produk harus milik brand user yang sedang login
    
    Logic:
    1. GET request: Tampilkan form tambah produk
    2. POST request:
       - Validasi data (name, category, price, stock, description)
       - Simpan produk ke database
       - Redirect ke dashboard dengan success message
    """
    current_toko = getattr(request.user, 'toko', None)
    if current_toko is None:
        messages.error(request, '❌ Profil toko Anda belum terdaftar! Silakan hubungi admin atau daftar toko terlebih dahulu.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        return render(request, 'master_products/add_product.html')
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM ====================
        name = request.POST.get('name', '').strip()
        category_name = request.POST.get('category', '').strip()
        price = request.POST.get('price', '').strip()
        stock = request.POST.get('stock', '').strip()
        description = request.POST.get('description', '').strip()
        
        # ==================== VALIDASI DATA ====================
        if not all([name, category_name, price, stock, description]):
            messages.error(request, 'Semua field harus diisi! Pastikan Nama, Kategori, Harga, Stok, dan Deskripsi sudah lengkap.')
            return render(request, 'master_products/add_product.html')
        
        # Validasi tipe data
        try:
            price = float(price)
            stock = int(stock)
            
            if price <= 0:
                messages.error(request, 'Harga produk harus lebih dari 0!')
                return render(request, 'master_products/add_product.html')
            
            if stock < 0:
                messages.error(request, 'Stok produk tidak boleh negatif!')
                return render(request, 'master_products/add_product.html')
        
        except ValueError:
            messages.error(request, 'Format harga atau stok tidak valid! Gunakan angka saja.')
            return render(request, 'master_products/add_product.html')
        
        # ==================== GET ATAU CREATE KATEGORI ====================
        # Mapping nama kategori ke model Category
        category_mapping = {
            'smartphone': 'Smartphone & Aksesoris',
            'laptop': 'Laptop & Notebook',
            'components': 'Komponen & Hardware',
            'smart_home': 'Smart Home & IoT',
            'audio': 'Audio & Multimedia',
            'gaming': 'Gaming Devices',
            'tv': 'TV & Monitor',
            'lainnya': 'Kategori Lainnya',
        }
        
        category_display_name = category_mapping.get(category_name, category_name)
        
        try:
            category = Category.objects.get(category_name=category_display_name)
        except Category.DoesNotExist:
            messages.error(request, f'Kategori "{category_display_name}" tidak ditemukan. Silakan pilih kategori yang valid.')
            return render(request, 'master_products/add_product.html')
        
        # ==================== SIMPAN PRODUK KE DATABASE ====================
        try:
            product = Product.objects.create(
                brand_id=current_toko,
                category_id=category,
                product_name=name,
                slug=name.lower().replace(' ', '-'),
                description=description,
                price=price,
                stock=stock,
                is_active=True
            )
            
            messages.success(request, f'Produk "{name}" berhasil ditambahkan ke katalog Anda! Produk akan tampil di dashboard dan dapat ditemukan pembeli.')
            return redirect('master_products:seller_dashboard')
        
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat menyimpan produk: {str(e)}')
            return render(request, 'master_products/add_product.html')


@login_required(login_url='master_products:login')
@seller_required
def edit_product(request, product_id):
    """
    Edit produk yang sudah ada di katalog penjual.
    
    Keamanan:
    - @login_required: User harus sudah login
    - @seller_required: User harus penjual yang disetujui
    - Ownership check: Produk harus milik brand penjual yang sedang login
    
    Logic:
    1. GET request: Tampilkan form edit dengan data produk lama
    2. POST request:
       - Validasi data (nama, kategori, harga, stok, deskripsi)
       - Update produk ke database dengan atomic transaction
       - Redirect ke seller dashboard dengan success message
    """
    
    # ==================== GET BRAND PENJUAL ====================
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    # ==================== GET PRODUK & VALIDASI OWNERSHIP ====================
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        messages.error(request, '❌ Produk tidak ditemukan!')
        return redirect('master_products:seller_dashboard')
    
    # Pastikan produk milik brand penjual yang login
    if product.brand_id != seller_brand:
        messages.error(request, '❌ Akses ditolak! Produk ini bukan milik Anda.')
        return redirect('master_products:seller_dashboard')
    
    if request.method == 'GET':
        # ==================== TAMPILKAN FORM EDIT ====================
        categories = Category.objects.all().order_by('category_name')
        context = {
            'product': product,
            'product_id': product.product_id,
            'current_name': product.product_name,
            'current_category': product.category_id.category_id,
            'current_price': product.price,
            'current_stock': product.stock,
            'current_description': product.description,
            'categories': categories,
        }
        return render(request, 'master_products/edit_product.html', context)
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM ====================
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category', '').strip()
        price = request.POST.get('price', '').strip()
        stock = request.POST.get('stock', '').strip()
        description = request.POST.get('description', '').strip()
        
        # ==================== VALIDASI DATA ====================
        if not all([name, category_id, price, stock, description]):
            messages.error(request, '❌ Semua field harus diisi!')
            return redirect('master_products:edit_product', product_id=product_id)
        
        # Validasi tipe data
        try:
            price = float(price)
            stock = int(stock)
            category_id = int(category_id)
            
            if price <= 0:
                messages.error(request, '❌ Harga produk harus lebih dari 0!')
                return redirect('master_products:edit_product', product_id=product_id)
            
            if stock < 0:
                messages.error(request, '❌ Stok produk tidak boleh negatif!')
                return redirect('master_products:edit_product', product_id=product_id)
        
        except (ValueError, TypeError):
            messages.error(request, '❌ Format harga, stok, atau kategori tidak valid!')
            return redirect('master_products:edit_product', product_id=product_id)
        
        # ==================== GET KATEGORI ====================
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            messages.error(request, '❌ Kategori tidak ditemukan!')
            return redirect('master_products:edit_product', product_id=product_id)
        
        # ==================== UPDATE PRODUK ====================
        try:
            with transaction.atomic():
                # Update fields
                product.product_name = name
                product.category_id = category
                product.price = price
                product.stock = stock
                product.description = description
                product.slug = name.lower().replace(' ', '-')
                
                # Save ke database
                product.save()
                
                messages.success(request, f'✅ Produk "{name}" berhasil diperbarui!')
                return redirect('master_products:seller_dashboard')
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat mengupdate produk: {str(e)}')
            return redirect('master_products:edit_product', product_id=product_id)


@login_required(login_url='master_products:login')
@seller_required
def delete_product(request, product_id):
    """
    Menghapus produk dari katalog penjual.
    
    Keamanan:
    - @login_required: User harus sudah login
    - @seller_required: User harus penjual yang disetujui
    - POST-only: Hanya terima POST request untuk menghindari accidental delete
    - Ownership check: Produk harus milik brand penjual yang sedang login
    
    Logic:
    - Validasi produk ada dan milik penjual
    - Hapus dengan atomic transaction
    - Tampilkan success message
    - Redirect ke seller dashboard
    """
    
    # ==================== HANYA TERIMA POST ====================
    if request.method != 'POST':
        messages.error(request, '❌ Metode request tidak valid!')
        return redirect('master_products:seller_dashboard')
    
    # ==================== GET BRAND PENJUAL ====================
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    # ==================== GET PRODUK & VALIDASI OWNERSHIP ====================
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        messages.error(request, '❌ Produk tidak ditemukan!')
        return redirect('master_products:seller_dashboard')
    
    # Pastikan produk milik brand penjual yang login
    if product.brand_id != seller_brand:
        messages.error(request, '❌ Akses ditolak! Produk ini bukan milik Anda.')
        return redirect('master_products:seller_dashboard')
    
    # ==================== HAPUS PRODUK ====================
    product_name = product.product_name  # Simpan nama sebelum dihapus
    
    try:
        with transaction.atomic():
            product.delete()
            messages.success(request, f'✅ Produk "{product_name}" berhasil dihapus dari katalog Anda!')
    
    except Exception as e:
        messages.error(request, f'❌ Terjadi kesalahan saat menghapus produk: {str(e)}')
    
    return redirect('master_products:seller_dashboard')


# ============================================================================
# CHECKOUT & PAYMENT VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def checkout_view(request):
    """
    Menampilkan halaman checkout dan memproses pembuatan order dari cart.
    
    Fitur:
    1. GET request: Tampilkan form checkout dengan data default user
    2. POST request: 
       - Validasi cart tidak kosong
       - Validasi stok produk (double-check sebelum commit)
       - Gunakan transaction.atomic() untuk memastikan data konsisten
       - Create Order dengan status 'pending' & payment_status 'pending'
       - Create OrderItem untuk setiap item di cart
       - Decrement product stock secara real-time
       - Clear cart items setelah berhasil
       - Redirect ke halaman pembayaran
    
    Keamanan:
    - @login_required: User harus sudah login
    - transaction.atomic(): Memastikan semua operasi commit atomically
    - Validasi stok double-check untuk race condition prevention
    """
    
    # ==================== GET ATAU BUAT CART UNTUK USER ====================
    try:
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id')
    except Cart.DoesNotExist:
        messages.error(request, '❌ Keranjang Anda kosong! Silakan tambahkan produk terlebih dahulu.')
        return redirect('master_products:product_list')
    
    # ==================== VALIDASI CART TIDAK KOSONG ====================
    if not cart_items.exists():
        messages.error(request, '❌ Keranjang Anda kosong! Silakan tambahkan produk terlebih dahulu.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        # ==================== HITUNG TOTAL CHECKOUT ====================
        total_price = 0
        total_items = 0
        
        for item in cart_items:
            item.subtotal = float(item.price) * item.qty
            total_price += item.subtotal
            total_items += item.qty
        
        # ==================== BUILD CONTEXT UNTUK FORM CHECKOUT ====================
        context = {
            'cart_items': cart_items,
            'total_items': total_items,
            'total_price': total_price,
            'total_price_formatted': f"Rp{total_price:,.0f}",
            'payment_methods': Order.PAYMENT_METHOD_CHOICES,
            'user_name': request.user.first_name or request.user.username,
            'user_email': request.user.email,
            'user_phone': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
        }
        
        return render(request, 'master_products/checkout.html', context)
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM CHECKOUT ====================
        receiver_name = request.POST.get('receiver_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        payment_method = request.POST.get('payment_method', '').strip()
        
        # ==================== VALIDASI DATA FORM ====================
        if not receiver_name:
            messages.error(request, '❌ Nama penerima harus diisi!')
            return redirect('master_products:checkout_view')
        
        if not phone or len(phone) < 9:
            messages.error(request, '❌ Nomor telepon harus diisi dengan format yang valid (minimal 9 digit)!')
            return redirect('master_products:checkout_view')
        
        if not shipping_address or len(shipping_address) < 10:
            messages.error(request, '❌ Alamat pengiriman harus diisi dengan lengkap (minimal 10 karakter)!')
            return redirect('master_products:checkout_view')
        
        if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
            messages.error(request, '❌ Metode pembayaran tidak valid! Silakan pilih metode yang tersedia.')
            return redirect('master_products:checkout_view')
        
        # ==================== MULAI TRANSACTION ATOMIC ====================
        try:
            with transaction.atomic():
                # ==================== 1. REFRESH CART ITEMS UNTUK MENGHINDARI RACE CONDITION ====================
                # Re-fetch dari database untuk memastikan data terbaru
                cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id')
                
                if not cart_items.exists():
                    messages.error(request, '❌ Keranjang Anda kosong! Silakan tambahkan produk terlebih dahulu.')
                    return redirect('master_products:product_list')
                
                # ==================== 2. VALIDASI STOK SEMUA PRODUK (DOUBLE-CHECK) ====================
                stock_errors = []
                for item in cart_items:
                    # Re-fetch produk untuk stok terbaru
                    product = Product.objects.select_for_update().get(product_id=item.product_id.product_id)
                    
                    if product.stock < item.qty:
                        stock_errors.append(
                            f"• '{product.product_name}': Stok tersedia {product.stock} unit, "
                            f"Anda pesan {item.qty} unit"
                        )
                
                if stock_errors:
                    error_msg = '⚠️ Stok produk tidak mencukupi untuk checkout:\n' + '\n'.join(stock_errors)
                    messages.warning(request, error_msg)
                    return redirect('master_products:view_cart')
                
                # ==================== 3. HITUNG TOTAL HARGA ====================
                total_amount = 0
                for item in cart_items:
                    subtotal = float(item.price) * item.qty
                    total_amount += subtotal
                
                if total_amount <= 0:
                    messages.error(request, '❌ Total harga tidak valid! Keranjang Anda kosong atau ada error.')
                    return redirect('master_products:view_cart')
                
                # ==================== 4. GET BRAND DARI ITEM PERTAMA ====================
                # Catatan: Untuk MVP ini, diasumsikan semua item dari 1 brand
                # Di masa depan bisa diperluas untuk multi-brand orders
                first_brand = cart_items.first().product_id.brand_id
                
                # ==================== 5. GENERATE ORDER CODE UNIK ====================
                # Format: ORD-TIMESTAMP-RANDOMHEX (contoh: ORD-1718000000-A1B2C3)
                order_code = f"ORD-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
                
                # Verifikasi order_code belum ada di database (extra safety)
                while Order.objects.filter(order_code=order_code).exists():
                    order_code = f"ORD-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
                
                # ==================== 6. CREATE ORDER OBJECT ====================
                order = Order.objects.create(
                    user_id=request.user,
                    brand_id=first_brand,
                    order_code=order_code,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    receiver_name=receiver_name,
                    phone=phone,
                    status='pending',  # Status awal
                    payment_status='pending'  # Belum dibayar
                )
                
                # ==================== 7. CREATE ORDER ITEMS & DECREMENT STOCK ====================
                for cart_item in cart_items:
                    # Create OrderItem dengan menyimpan harga dan qty saat order dibuat
                    OrderItem.objects.create(
                        order_id=order,
                        product_id=cart_item.product_id,
                        price=cart_item.price,
                        qty=cart_item.qty
                    )
                    
                    # Decrement product stock (PENTING: gunakan F() untuk atomic decrement)
                    product = cart_item.product_id
                    product.stock = F('stock') - cart_item.qty
                    product.save(update_fields=['stock'])
                
                # ==================== 8. DELETE CART ITEMS ====================
                cart_items.delete()
                
                # ==================== 9. SUCCESS MESSAGE & REDIRECT ====================
                success_msg = (
                    f'✅ Pesanan Anda berhasil dibuat!<br>'
                    f'<strong>Kode Pesanan:</strong> {order_code}<br>'
                    f'<strong>Total Pembayaran:</strong> Rp{total_amount:,.0f}<br>'
                    f'<strong>Status:</strong> Menunggu Pembayaran<br>'
                    f'Silakan lanjutkan ke halaman pembayaran untuk menyelesaikan transaksi.'
                )
                messages.success(request, success_msg)
                
                # Redirect ke halaman payment gateway simulator untuk proses payment
                return redirect('master_products:payment_gateway_view', order_id=order.order_id)
        
        except Exception as e:
            # Rollback otomatis karena atomic() error
            messages.error(request, f'❌ Terjadi kesalahan saat membuat pesanan: {str(e)}')
            return redirect('master_products:checkout_view')


@login_required(login_url='master_products:login')
def payment_gateway_view(request, order_id):
    """
    Halaman Intermediari Payment Gateway Simulator.
    
    Fitur:
    1. GET request: Tampilkan halaman simulator pembayaran dengan:
       - Ringkasan tagihan (order details)
       - Nomor Virtual Account dummy (Mandiri VA / BCA VA)
       - QRIS dummy code
       - Tombol "SIMULASIKAN BAYAR SUKSES"
    
    2. POST request (Simulasi Bayar Sukses):
       - Validasi user memiliki order tersebut
       - Update order status menjadi 'confirmed' & payment_status 'paid'
       - Kurangi stok produk (atomic)
       - Redirect ke halaman invoice
    
    URL Parameters:
    - order_id: ID order yang ingin dibayar
    """
    
    # ==================== GET ORDER ====================
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    # ==================== VALIDASI PERMISSION ====================
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        # ==================== GET ORDER ITEMS ====================
        order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
        
        # Generate dummy payment references
        va_mandiri = f"888{order.order_id:06d}"
        va_bca = f"777{order.order_id:06d}"
        qris_code = f"00020126360014com.midtrans{order.order_id:06d}520400005303360"
        
        # ==================== BUILD CONTEXT UNTUK HALAMAN PAYMENT GATEWAY ====================
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
            'brand_name': order.brand_id.brand_name,
            'va_mandiri': va_mandiri,
            'va_bca': va_bca,
            'qris_code': qris_code,
            'order_date': order.order_date,
        }
        
        return render(request, 'master_products/payment_gateway.html', context)
    
    if request.method == 'POST':
        # ==================== PROSES SIMULASI BAYAR SUKSES ====================
        try:
            with transaction.atomic():
                # ==================== 1. VALIDASI ORDER STATUS ====================
                if order.payment_status == 'paid':
                    messages.warning(request, '⚠️ Order ini sudah dibayar sebelumnya!')
                    return redirect('master_products:invoice_view', order_id=order.order_id)
                
                # ==================== 2. UPDATE ORDER STATUS KE PAID ====================
                order.status = 'confirmed'
                order.payment_status = 'paid'
                order.save()
                
                # ==================== 3. KURANGI STOK PRODUK (ATOMIC) ====================
                order_items = order.items.all().select_related('product_id')
                for item in order_items:
                    product = Product.objects.select_for_update().get(product_id=item.product_id.product_id)
                    product.stock = F('stock') - item.qty
                    product.save(update_fields=['stock'])
                
                # ==================== SUCCESS MESSAGE ====================
                success_msg = (
                    f'✅ <strong>TRANSAKSI BERHASIL!</strong><br><br>'
                    f'Pesanan Anda dari <strong>{order.brand_id.brand_name} Purwokerto</strong> sedang diproses.<br><br>'
                    f'• Kode Pesanan: <strong>{order.order_code}</strong><br>'
                    f'• Total Pembayaran: <strong>Rp{order.total_amount:,.0f}</strong><br>'
                    f'• Status: <strong>Lunas - Pesanan Sedang Dikemas oleh Toko</strong>'
                )
                messages.success(request, success_msg)
                
                # ==================== REDIRECT KE INVOICE ====================
                return redirect('master_products:invoice_view', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat memproses pembayaran: {str(e)}')
            return redirect('master_products:payment_gateway_view', order_id=order.order_id)


@login_required(login_url='master_products:login')
def invoice_view(request, order_id):
    """
    Halaman Invoice / Bukti Pembayaran.
    
    Menampilkan:
    - Nomor Pesanan Unik
    - Tanggal Transaksi
    - Detail Produk yang dibeli beserta nama Toko Purwokerto
    - Alamat Pengiriman
    - Status: "Lunas - Pesanan Sedang Dikemas oleh Toko"
    - Tombol Download Invoice (PDF) atau Print
    
    Desain: Clean, professional, dan siap dicetak
    """
    
    # ==================== GET ORDER ====================
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    # ==================== VALIDASI PERMISSION ====================
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Invoice ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    # ==================== GET ORDER ITEMS ====================
    order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
    
    # ==================== BUILD CONTEXT UNTUK INVOICE ====================
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
        'brand_name': order.brand_id.brand_name,
        'brand_address': order.brand_id.address if hasattr(order.brand_id, 'address') else 'Purwokerto',
        'order_date': order.order_date,
        'is_paid': order.payment_status == 'paid',
    }
    
    return render(request, 'master_products/invoice.html', context)


@login_required(login_url='master_products:login')
def process_payment_view(request, order_id):
    """
    Halaman pembayaran lama (deprecated - redirect ke payment_gateway_view).
    
    Fitur:
    1. GET request: Tampilkan form pembayaran dengan detail order
    2. POST request (Dummy Payment Simulator):
       - Validasi user memiliki order tersebut
       - Update order status menjadi 'confirmed' (payment_status: 'paid')
       - Redirect ke halaman konfirmasi dengan order details
    
    URL Parameters:
    - order_id: ID order yang ingin dibayar
    
    Keamanan:
    - @login_required: User harus sudah login
    - Permission check: User hanya bisa bayar order mereka sendiri
    """
    
    # ==================== GET ORDER ====================
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    # ==================== VALIDASI PERMISSION ====================
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    if request.method == 'GET':
        # ==================== GET ORDER ITEMS ====================
        order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
        
        # ==================== BUILD CONTEXT UNTUK HALAMAN PEMBAYARAN ====================
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
        # ==================== DUMMY PAYMENT SIMULATOR (PRODUCTION: Integrate Midtrans/Stripe) ====================
        # Untuk MVP ini: simulasi payment success
        # Catatan: Di production, integrate dengan payment gateway (Midtrans, Stripe, dll)
        
        try:
            # ==================== UPDATE ORDER STATUS KE CONFIRMED ====================
            order.status = 'confirmed'
            order.payment_status = 'paid'
            order.save()
            
            # ==================== BUILD SUCCESS MESSAGE SESUAI REQUIREMENT ====================
            brand_name = order.brand_id.brand_name
            
            success_msg = (
                f'✅ <strong>TRANSAKSI BERHASIL!</strong><br><br>'
                f'Pesanan Anda dari <strong>{brand_name} Purwokerto</strong> sedang diproses.<br><br>'
                f'<strong>Detail Pesanan:</strong><br>'
                f'• Kode Pesanan: <strong>{order.order_code}</strong><br>'
                f'• Total Pembayaran: <strong>Rp{order.total_amount:,.0f}</strong><br>'
                f'• Metode Pembayaran: <strong>{dict(Order.PAYMENT_METHOD_CHOICES)[order.payment_method]}</strong><br>'
                f'• Status: <strong>Menunggu Konfirmasi Penjual</strong><br><br>'
                f'Anda akan menerima notifikasi via email dan SMS sesuai perkembangan pesanan.'
            )
            messages.success(request, success_msg)
            
            # ==================== REDIRECT KE HALAMAN KONFIRMASI ====================
            return redirect('master_products:order_confirmation', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat memproses pembayaran: {str(e)}')
            return redirect('master_products:process_checkout', order_id=order.order_id)


@login_required(login_url='master_products:login')
def order_confirmation_view(request, order_id):
    """
    Menampilkan halaman konfirmasi order setelah pembayaran sukses.
    
    Fitur:
    1. Tampilkan detail order lengkap
    2. Tampilkan list OrderItem dengan qty & harga
    3. Tampilkan total pembayaran dan metode pembayaran
    4. Tombol untuk kembali ke katalog atau lihat order history
    
    URL Parameters:
    - order_id: ID order untuk ditampilkan
    
    Keamanan:
    - @login_required: User harus sudah login
    - Permission check: User hanya bisa lihat order mereka
    """
    
    # ==================== GET ORDER ====================
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:product_list')
    
    # ==================== VALIDASI PERMISSION ====================
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:product_list')
    
    # ==================== GET ORDER ITEMS ====================
    order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
    
    # ==================== BUILD CONTEXT ====================
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


@login_required(login_url='master_products:login')
def order_list_view(request):
    """
    Menampilkan halaman list semua order milik customer yang login.
    
    Fitur:
    1. Tampilkan semua order dengan status
    2. Sort by order date (terbaru duluan)
    3. Link ke detail order
    4. Filter by status (optional)
    """
    
    # ==================== GET ALL ORDERS UNTUK USER ====================
    orders = Order.objects.filter(
        user_id=request.user
    ).select_related('brand_id').order_by('-order_date')
    
    # ==================== BUILD CONTEXT ====================
    context = {
        'orders': orders,
        'total_orders': orders.count(),
    }
    
    return render(request, 'master_products/order_list.html', context)


@login_required(login_url='master_products:login')
def order_detail_view(request, order_id):
    """
    Menampilkan halaman detail order dengan OrderItem lengkap.
    
    Fitur:
    1. Tampilkan detail order (alamat, pembayaran, status)
    2. Tampilkan list OrderItem
    3. Timeline status pengiriman (future: integrate dengan courier API)
    4. Tombol untuk resi/tracking (future)
    """
    
    # ==================== GET ORDER ====================
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, '❌ Order tidak ditemukan!')
        return redirect('master_products:order_list')
    
    # ==================== VALIDASI PERMISSION ====================
    if order.user_id != request.user:
        messages.error(request, '❌ Akses ditolak! Order ini bukan milik Anda.')
        return redirect('master_products:order_list')
    
    # ==================== GET ORDER ITEMS ====================
    order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
    
    # ==================== BUILD CONTEXT ====================
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


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def submit_review(request, product_id):
    """
    Menerima dan menyimpan review produk dari customer.
    
    POST Parameters:
    - rating: 1-5 (required)
    - comment: text review (optional)
    
    Response: JSON redirect atau pesan success
    """
    product = get_object_or_404(Product, product_id=product_id)
    
    try:
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        
        # Validasi rating
        if rating < 1 or rating > 5:
            messages.error(request, '❌ Rating harus antara 1-5!')
            return redirect('master_products:product_detail_by_id', product_id=product_id)
        
        # Hapus review lama (1 user = 1 review per produk)
        Review.objects.filter(product_id=product, user_id=request.user).delete()
        
        # Buat review baru
        Review.objects.create(
            product_id=product,
            user_id=request.user,
            rating=rating,
            comment=comment if comment else None
        )
        
        messages.success(request, f'✅ Terima kasih! Ulasan Anda dengan rating {rating}⭐ berhasil disimpan.')
    
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    
    return redirect('master_products:product_detail_by_id', product_id=product_id)


# ============================================================================
# USER PROFILE VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
def user_profile_view(request):
    """
    Menampilkan halaman profil user dengan informasi pribadi dan alamat.
    
    Fitur:
    1. Tampilkan informasi pribadi user (nama, email, username)
    2. Edit informasi pribadi (nama depan/belakang)
    3. Tampilkan alamat utama Purwokerto
    4. Link ke order history
    5. Link untuk ubah password
    """
    
    # ==================== GET USER DATA ====================
    user = request.user
    
    # ==================== HANDLE POST REQUEST (UPDATE PROFILE) ====================
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        try:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, '✅ Profil Anda berhasil diperbarui!')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        
        return redirect('master_products:user_profile')
    
    # ==================== BUILD CONTEXT ====================
    two_factor, created = UserTwoFactor.objects.get_or_create(user=request.user)
    
    active_sessions_count = LoginSession.objects.filter(
        user=request.user,
        is_active=True
    ).count()
    
    context = {
        'user': user,
        'two_factor': two_factor,
        'active_sessions_count': active_sessions_count,
    }
    
    return render(request, 'master_products/profile.html', context)


@login_required(login_url='master_products:login')
def enable_2fa(request):
    """Aktifkan Two-Factor Authentication untuk user saat ini."""
    two_factor, created = UserTwoFactor.objects.get_or_create(user=request.user)
    two_factor.is_enabled = True
    two_factor.save()
    messages.success(request, 'Two-Factor Authentication berhasil diaktifkan')
    return redirect('master_products:user_profile')


@login_required(login_url='master_products:login')
def disable_2fa(request):
    """Nonaktifkan Two-Factor Authentication untuk user saat ini."""
    two_factor, created = UserTwoFactor.objects.get_or_create(user=request.user)
    two_factor.is_enabled = False
    two_factor.save()
    messages.success(request, 'Two-Factor Authentication berhasil dinonaktifkan')
    return redirect('master_products:user_profile')


@login_required(login_url='master_products:login')
@seller_required
def seller_products(request):
    """Halaman kelola produk untuk penjual."""
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    products = Product.objects.filter(brand_id=seller_brand).order_by('-created_at')
    
    context = {
        'seller_brand': seller_brand,
        'products': products,
        'total_products': products.count(),
    }
    
    return render(request, 'master_products/seller_products.html', context)


@login_required(login_url='master_products:login')
@seller_required
def seller_orders(request):
    """Halaman kelola pesanan untuk penjual."""
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    orders = Order.objects.filter(brand_id=seller_brand).order_by('-order_date')
    
    context = {
        'seller_brand': seller_brand,
        'orders': orders,
        'total_orders': orders.count(),
    }
    
    return render(request, 'master_products/seller_orders.html', context)


@login_required(login_url='master_products:login')
@seller_required
def seller_order_detail(request, order_id):
    """Detail pesanan untuk penjual."""
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    try:
        order = Order.objects.get(order_id=order_id, brand_id=seller_brand)
    except Order.DoesNotExist:
        messages.error(request, '❌ Pesanan tidak ditemukan!')
        return redirect('master_products:seller_orders')
    
    order_items = order.items.all().select_related('product_id')
    
    context = {
        'seller_brand': seller_brand,
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'master_products/seller_order_detail.html', context)


@login_required
@seller_required
@require_http_methods(["POST"])
def seller_order_update(request, order_id):
    """Update status pesanan untuk penjual."""
    try:
        seller_brand = Brand.objects.get(user_id=request.user)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Profil brand Anda belum terdaftar!')
        return redirect('master_products:product_list')
    
    try:
        order = Order.objects.get(order_id=order_id, brand_id=seller_brand)
    except Order.DoesNotExist:
        messages.error(request, '❌ Pesanan tidak ditemukan!')
        return redirect('master_products:seller_orders')
    
    # Get new status from form
    new_status = request.POST.get('status', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()
    cancel_reason = request.POST.get('cancel_reason', '').strip()
    
    # Validate status
    valid_statuses = ['confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
    if not new_status or new_status not in valid_statuses:
        messages.error(request, '❌ Status pesanan tidak valid!')
        return redirect('master_products:seller_order_detail', order_id=order_id)
    
    # Update order status
    old_status = order.status
    order.status = new_status
    
    # Add tracking number if provided
    if tracking_number and new_status == 'shipped':
        order.tracking_number = tracking_number
    
    # Add cancel reason if cancelling
    if new_status == 'cancelled' and cancel_reason:
        order.cancel_reason = cancel_reason
    
    # Save order
    order.save()
    
    # Log status change
    status_display = dict(Order._meta.get_field('status').choices).get(new_status, new_status)
    messages.success(request, f'✅ Status pesanan berhasil diperbarui menjadi: {status_display}')
    
    return redirect('master_products:seller_order_detail', order_id=order_id)


# ============================================================================
# ADMIN PANEL VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
def admin_panel_view(request):
    """
    Admin panel untuk mengelola mitra dan pengguna VOLTA.
    
    Fitur:
    1. Verifikasi mitra yang menunggu
    2. List mitra terverifikasi
    3. Manajemen pengguna global
    
    Hanya bisa diakses oleh superuser.
    """
    
    # ==================== VALIDASI SUPERUSER ====================
    if not request.user.is_superuser:
        messages.error(request, '❌ Akses Ditolak! Hanya superuser yang dapat mengakses.')
        return redirect('master_products:product_list')
    
    # ==================== GET BRANDS DATA ====================
    total_brands = Brand.objects.count()
    verified_brands = Brand.objects.filter(status='approved').count()
    pending_brands = Brand.objects.filter(status='pending').count()
    
    pending_verification_brands = Brand.objects.filter(status='pending').select_related('user_id')
    verified_brands_list = Brand.objects.filter(status='approved').select_related('user_id').prefetch_related('products')
    
    # ==================== GET USERS DATA ====================
    total_users = User.objects.count()
    all_users = User.objects.all().order_by('-date_joined')[:50]
    
    # ==================== BUILD CONTEXT ====================
    context = {
        'total_brands': total_brands,
        'verified_brands': verified_brands,
        'pending_brands': pending_brands,
        'pending_verification_brands': pending_verification_brands,
        'verified_brands_list': verified_brands_list,
        'total_users': total_users,
        'all_users': all_users,
    }
    
    return render(request, 'master_products/admin_panel.html', context)


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def admin_verify_brand(request, brand_id):
    """
    Verifikasi brand dan ubah status menjadi 'approved'.
    Ini akan membuat badge hijau "Mitra Terverifikasi VOLTA" muncul di store detail page.
    """
    
    if not request.user.is_superuser:
        messages.error(request, '❌ Akses Ditolak!')
        return redirect('master_products:product_list')
    
    try:
        brand = Brand.objects.get(brand_id=brand_id)
        brand.status = 'approved'
        brand.save()
        messages.success(request, f'✅ {brand.brand_name} berhasil diverifikasi!')
    except Brand.DoesNotExist:
        messages.error(request, '❌ Brand tidak ditemukan!')
    
    return redirect('master_products:admin_panel')


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def admin_reject_brand(request, brand_id):
    """
    Tolak verifikasi brand dan ubah status menjadi 'rejected'.
    """
    
    if not request.user.is_superuser:
        messages.error(request, '❌ Akses Ditolak!')
        return redirect('master_products:product_list')
    
    try:
        brand = Brand.objects.get(brand_id=brand_id)
        brand.status = 'rejected'
        brand.save()
        messages.success(request, f'❌ {brand.brand_name} berhasil ditolak.')
    except Brand.DoesNotExist:
        messages.error(request, '❌ Brand tidak ditemukan!')
    
    return redirect('master_products:admin_panel')


# ============================================================================
# ADMIN PLATFORM VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
def admin_platform_dashboard(request):
    """
    Dashboard Admin Platform VOLTA - Real-time Metrics & Management.
    
    Menampilkan:
    1. Total Brand Terdaftar (semua status)
    2. Brand Menunggu Persetujuan (pending)
    3. Total Customer Aktif
    4. Total Transaksi Bulan Ini
    5. Total Revenue Platform
    6. Tabel: Brand Menunggu Persetujuan (pending) dengan tombol Approve/Reject
    7. Tabel: Brand yang Sudah Aktif
    
    Hanya bisa diakses oleh admin.
    """
    
    # ==================== VALIDASI ADMIN ====================
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:product_list')
    
    # ==================== HITUNG METRICS ====================
    
    # 1. Total Brand (all statuses)
    total_brands = Brand.objects.count()
    
    # 2. Vendor Requests Pending Approval
    pending_vendor_requests = VendorRequest.objects.filter(status='Pending').count()
    
    # 3. Total Users
    total_users = User.objects.count()
    
    # 4. Active Sellers
    active_sellers = Brand.objects.filter(status='approved').count()
    
    # 5. Total Customer Aktif
    total_customers = User.objects.filter(role='customer', is_active=True).count()
    
    # 6. Total Transaksi (orders) bulan ini
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_transactions_month = Order.objects.filter(
        order_date__gte=first_day_month
    ).count()
    
    # 5. Total Revenue (dari semua orders)
    from django.db.models import Sum
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'processing', 'shipped', 'delivered'],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # 6. Daftar transaksi terbaru untuk dashboard
    recent_transactions = Order.objects.select_related('user_id', 'brand_id').order_by('-order_date')[:10]
    
    # ==================== GET PENDING VENDOR REQUESTS ====================
    pending_vendor_requests_list = VendorRequest.objects.filter(
        status='Pending'
    ).select_related('user').order_by('-created_at')[:25]
    
    # ==================== GET PRODUCTS FOR MODERATION ====================
    product_moderation_list = Product.objects.select_related('brand_id').order_by('-created_at')[:25]
    
    # ==================== GET USERS FOR MANAGEMENT ====================
    all_users = User.objects.order_by('-created_at')[:25]
    
    # ==================== GET APPROVED BRANDS (untuk tabel tambahan) ====================
    approved_brands_list = Brand.objects.filter(
        status='approved'
    ).select_related('user_id').order_by('-created_at')[:10]  # Top 10 approved brands
    
    # ==================== BUILD CONTEXT ====================
    context = {
        # Metrics
        'total_brands': total_brands,
        'total_users': total_users,
        'active_sellers': active_sellers,
        'pending_vendor_requests': pending_vendor_requests,
        'total_customers': total_customers,
        'total_transactions_month': total_transactions_month,
        'total_revenue': total_revenue,
        'total_revenue_formatted': f"Rp{total_revenue:,.0f}",
        
        # Data untuk tabel
        'pending_vendor_requests_list': pending_vendor_requests_list,
        'product_moderation_list': product_moderation_list,
        'recent_transactions': recent_transactions,
        'all_users': all_users,
        'approved_brands_list': approved_brands_list,
    }
    
    return render(request, 'master_products/admin_dashboard.html', context)


@login_required(login_url='master_products:login')
def approve_seller(request, seller_id):
    """
    View untuk menyetujui aplikasi penjual baru (ubah status Brand menjadi 'approved').
    
    Hanya menerima POST request dengan CSRF token untuk keamanan.
    Menggunakan atomic transaction untuk memastikan konsistensi data.
    
    URL Parameters:
    - seller_id: Brand ID yang akan disetujui
    
    Keamanan:
    - @login_required: Admin harus login
    - Role check: Hanya admin yang bisa approve
    - CSRF token required (POST only)
    - Atomic transaction untuk data integrity
    """
    
    # ==================== VALIDASI METHOD ====================
    if request.method != 'POST':
        messages.error(request, '❌ Method tidak diizinkan!')
        return redirect('master_products:admin_platform_dashboard')
    
    # ==================== VALIDASI ADMIN ====================
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:product_list')
    
    # ==================== GET BRAND ====================
    try:
        brand = Brand.objects.get(brand_id=seller_id)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Brand tidak ditemukan!')
        return redirect('master_products:admin_platform_dashboard')
    
    # ==================== MULAI TRANSACTION ====================
    try:
        with transaction.atomic():
            # ==================== UPDATE BRAND STATUS ====================
            brand.status = 'approved'
            brand.approved_at = timezone.now()
            brand.approved_by = request.user
            brand.save()
            
            # ==================== SUCCESS MESSAGE ====================
            messages.success(
                request,
                f'✅ Brand "{brand.brand_name}" berhasil disetujui! '
                f'User {brand.user_id.username} sekarang bisa menambahkan produk dan berjualan di platform.'
            )
    
    except Exception as e:
        messages.error(request, f'❌ Terjadi kesalahan: {str(e)}')
    
    # ==================== REDIRECT KE DASHBOARD ====================
    return redirect('master_products:admin_platform_dashboard')


@login_required(login_url='master_products:login')
def reject_seller(request, seller_id):
    """
    View untuk menolak aplikasi penjual baru (ubah status Brand menjadi 'rejected').
    
    Hanya menerima POST request dengan CSRF token untuk keamanan.
    Menggunakan atomic transaction untuk memastikan konsistensi data.
    
    URL Parameters:
    - seller_id: Brand ID yang akan ditolak
    
    Keamanan:
    - @login_required: Admin harus login
    - Role check: Hanya admin yang bisa reject
    - CSRF token required (POST only)
    - Atomic transaction untuk data integrity
    """
    
    # ==================== VALIDASI METHOD ====================
    if request.method != 'POST':
        messages.error(request, '❌ Method tidak diizinkan!')
        return redirect('master_products:admin_platform_dashboard')
    
    # ==================== VALIDASI ADMIN ====================
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:product_list')
    
    # ==================== GET BRAND ====================
    try:
        brand = Brand.objects.get(brand_id=seller_id)
    except Brand.DoesNotExist:
        messages.error(request, '❌ Brand tidak ditemukan!')
        return redirect('master_products:admin_platform_dashboard')
    
    # ==================== MULAI TRANSACTION ====================
    try:
        with transaction.atomic():
            # ==================== UPDATE BRAND STATUS ====================
            brand.status = 'rejected'
            brand.approved_by = request.user
            brand.save()
            
            # ==================== SUCCESS MESSAGE ====================
            messages.success(
                request,
                f'⚠️ Brand "{brand.brand_name}" berhasil ditolak. '
                f'User {brand.user_id.username} akan menerima notifikasi penolakan via email.'
            )
    
    except Exception as e:
        messages.error(request, f'❌ Terjadi kesalahan: {str(e)}')
    
    # ==================== REDIRECT KE DASHBOARD ====================
    return redirect('master_products:admin_platform_dashboard')


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def approve_vendor_request(request, request_id):
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:admin_platform_dashboard')

    try:
        vendor_request = VendorRequest.objects.get(id=request_id)

        if vendor_request.status == 'Rejected':
            messages.error(request, f'❌ Pengajuan vendor "{vendor_request.vendor_name}" sudah ditolak.')
            return redirect('master_products:admin_platform_dashboard')

        if not vendor_request.activation_token:
            vendor_request.activation_token = uuid.uuid4().hex
        vendor_request.token_created_at = timezone.now()
        vendor_request.status = 'Approved'
        vendor_request.save()

        activation_url = request.build_absolute_uri(
            reverse('master_products:vendor_setup_account', args=[vendor_request.activation_token])
        )

        subject = f'Aktivasi Akun Vendor VOLTA: {vendor_request.vendor_name}'
        message = (
            f'Halo {vendor_request.vendor_name},\n\n'
            f'Pengajuan kemitraan Anda telah disetujui oleh tim admin VOLTA.\n'
            f'Silakan lanjutkan pembuatan akun vendor dengan membuka tautan berikut:\n\n'
            f'{activation_url}\n\n'
            'Jika Anda tidak mengajukan kemitraan ini, abaikan email ini.\n\n'
            'Salam,\nTim VOLTA'
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [vendor_request.email],
                fail_silently=False,
            )
            messages.success(request, f'✅ Pengajuan vendor "{vendor_request.vendor_name}" berhasil disetujui dan email aktivasi dikirim ke {vendor_request.email}.')
        except Exception as email_error:
            messages.warning(
                request,
                f'✅ Pengajuan vendor "{vendor_request.vendor_name}" disetujui, tetapi terjadi masalah saat mengirim email: {str(email_error)}'
            )
    except VendorRequest.DoesNotExist:
        messages.error(request, '❌ Pengajuan vendor tidak ditemukan.')

    return redirect('master_products:admin_platform_dashboard')


@require_http_methods(["GET", "POST"])
def vendor_setup_account(request, token):
    try:
        vendor_request = VendorRequest.objects.get(activation_token=token, status='Approved')
    except VendorRequest.DoesNotExist:
        messages.error(request, '❌ Token aktivasi tidak valid atau sudah kadaluwarsa.')
        return redirect('master_products:product_list')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not password or not confirm_password:
            messages.error(request, '❌ Mohon isi password dan konfirmasi password.')
            return render(request, 'master_products/vendor_setup_account.html', {'vendor_request': vendor_request})

        if password != confirm_password:
            messages.error(request, '❌ Password dan konfirmasi password tidak cocok.')
            return render(request, 'master_products/vendor_setup_account.html', {'vendor_request': vendor_request})

        existing_user = User.objects.filter(email=vendor_request.email).first()
        if existing_user:
            existing_user.role = 'brand'
            existing_user.is_active = True
            existing_user.set_password(password)
            existing_user.save()
            user = existing_user
        else:
            user = User.objects.create_user(
                username=vendor_request.email,
                email=vendor_request.email,
                password=password,
                role='brand',
                first_name=vendor_request.vendor_name.split()[0] if vendor_request.vendor_name else '',
                last_name=' '.join(vendor_request.vendor_name.split()[1:]) if len(vendor_request.vendor_name.split()) > 1 else ''
            )

        if not hasattr(user, 'brand_vendor'):
            Brand.objects.create(
                user_id=user,
                brand_name=vendor_request.vendor_name,
                status='approved',
                approved_at=timezone.now(),
                approved_by=request.user if request.user.is_authenticated and request.user.role == 'admin' else None,
                nib_or_ktp=vendor_request.nib,
                description=vendor_request.description,
            )

        vendor_request.activation_token = None
        vendor_request.save()

        messages.success(request, '✅ Akun vendor berhasil dibuat. Silakan login menggunakan email Anda.')
        return redirect('master_products:login')

    return render(request, 'master_products/vendor_setup_account.html', {'vendor_request': vendor_request})


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def reject_vendor_request(request, request_id):
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:admin_platform_dashboard')

    try:
        vendor_request = VendorRequest.objects.get(id=request_id)
        vendor_request.status = 'Rejected'
        vendor_request.save()
        messages.success(request, f'⚠️ Pengajuan vendor "{vendor_request.vendor_name}" berhasil ditolak.')
    except VendorRequest.DoesNotExist:
        messages.error(request, '❌ Pengajuan vendor tidak ditemukan.')

    return redirect('master_products:admin_platform_dashboard')


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def deactivate_product(request, product_id):
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:admin_platform_dashboard')

    try:
        product = Product.objects.get(product_id=product_id)
        product.is_active = False
        product.save()
        messages.success(request, f'✅ Produk "{product.product_name}" berhasil dinonaktifkan.')
    except Product.DoesNotExist:
        messages.error(request, '❌ Produk tidak ditemukan.')

    return redirect('master_products:admin_platform_dashboard')


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def suspend_user(request, user_id):
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:admin_platform_dashboard')

    if request.user.id == user_id:
        messages.error(request, '❌ Anda tidak bisa mendiskors diri sendiri.')
        return redirect('master_products:admin_platform_dashboard')

    try:
        target_user = User.objects.get(pk=user_id)
        if target_user.is_superuser:
            messages.error(request, '❌ Tidak boleh mendiskors superuser.')
            return redirect('master_products:admin_platform_dashboard')
        target_user.is_active = False
        target_user.save()
        messages.success(request, f'⚠️ User "{target_user.username}" berhasil diskors.')
    except User.DoesNotExist:
        messages.error(request, '❌ User tidak ditemukan.')

    return redirect('master_products:admin_platform_dashboard')


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def delete_user(request, user_id):
    if request.user.role != 'admin' or not request.user.is_staff:
        messages.error(request, '❌ Akses Ditolak! Anda tidak memiliki izin sebagai admin.')
        return redirect('master_products:admin_platform_dashboard')

    if request.user.id == user_id:
        messages.error(request, '❌ Anda tidak bisa menghapus diri sendiri.')
        return redirect('master_products:admin_platform_dashboard')

    try:
        target_user = User.objects.get(pk=user_id)
        if target_user.is_superuser:
            messages.error(request, '❌ Tidak boleh menghapus superuser.')
            return redirect('master_products:admin_platform_dashboard')
        username = target_user.username
        target_user.delete()
        messages.success(request, f'❌ User "{username}" berhasil dihapus.')
    except User.DoesNotExist:
        messages.error(request, '❌ User tidak ditemukan.')

    return redirect('master_products:admin_platform_dashboard')


# ============================================================================
# USER PROFILE MANAGEMENT VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
def user_profile(request):
    user = request.user
    context = {
        'user': user,
        'role_display': dict(user._meta.get_field('role').choices).get(user.role, user.role),
        'member_since': user.created_at.strftime('%d %B %Y') if user.created_at else 'N/A',
    }
    return render(request, 'master_products/user_profile.html', context)


@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(user_id=user.user_id).exists():
                messages.error(request, 'Email sudah terdaftar!')
                return redirect('master_products:edit_profile')
        
        if phone and phone != user.phone:
            if User.objects.filter(phone=phone).exclude(user_id=user.user_id).exists():
                messages.error(request, 'Nomor telepon sudah terdaftar!')
                return redirect('master_products:edit_profile')
        
        if full_name:
            user.full_name = full_name
        if email:
            user.email = email
        if phone:
            user.phone = phone
        
        user.save()
        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('master_products:user_profile')
    
    context = {
        'user': user,
        'role_display': dict(user._meta.get_field('role').choices).get(user.role, user.role),
    }
    return render(request, 'master_products/edit_profile.html', context)


@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def update_address(request):
    user = request.user
    if request.method == 'POST':
        address_street = request.POST.get('address_street', '').strip()
        address_city = request.POST.get('address_city', '').strip()
        address_province = request.POST.get('address_province', '').strip()
        address_postal_code = request.POST.get('address_postal_code', '').strip()

        user.address_street = address_street
        user.address_city = address_city
        user.address_province = address_province
        user.address_postal_code = address_postal_code
        user.save()

        messages.success(request, 'Alamat berhasil diperbarui!')
        return redirect('master_products:user_profile')

    context = {
        'user': user,
        'role_display': dict(user._meta.get_field('role').choices).get(user.role, user.role),
    }
    return render(request, 'master_products/update_address.html', context)


@login_required(login_url='master_products:login')
@require_http_methods(["GET", "POST"])
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Password lama tidak sesuai!')
            return redirect('master_products:change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Password baru tidak cocok!')
            return redirect('master_products:change_password')
        
        if len(new_password) < 6:
            messages.error(request, 'Password minimal 6 karakter!')
            return redirect('master_products:change_password')
        
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password berhasil diubah! Silakan login kembali.')
        return redirect('master_products:login')
    
    return render(request, 'master_products/change_password.html')


# ============================================================================
# CART MANAGEMENT VIEWS
# ============================================================================

@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def update_cart_item(request):
    try:
        from decimal import Decimal
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = int(data.get('quantity', 1))
        
        if new_quantity < 1:
            new_quantity = 1
        if new_quantity > 999:
            new_quantity = 999
        
        try:
            cart = Cart.objects.get(user_id=request.user)
            cart_item = CartItem.objects.get(cart_item_id=item_id, cart_id=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Item tidak ditemukan'}, status=404)
        
        product = cart_item.product_id
        if product.stock < new_quantity:
            return JsonResponse({'status': 'error', 'message': f'Stok hanya tersedia {product.stock} unit'}, status=400)
        
        cart_item.qty = new_quantity
        cart_item.save()
        
        cart_total = cart.items.aggregate(
            total=Sum(F('product_id__price') * F('qty'), output_field=models.DecimalField())
        )['total'] or Decimal('0.00')
        
        return JsonResponse({'status': 'success', 'message': f'Quantity diperbarui', 'new_quantity': new_quantity, 'cart_total': str(cart_total)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url='master_products:login')
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    try:
        from decimal import Decimal
        cart = Cart.objects.get(user_id=request.user)
        cart_item = CartItem.objects.get(cart_item_id=item_id, cart_id=cart)
        product_name = cart_item.product_id.product_name
        cart_item.delete()
        
        cart_total = cart.items.aggregate(
            total=Sum(F('product_id__price') * F('qty'), output_field=models.DecimalField())
        )['total'] or Decimal('0.00')
        
        return JsonResponse({'status': 'success', 'message': f'"{product_name}" dihapus', 'cart_total': str(cart_total)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ============================================================================
# CUSTOMER SERVICE VIEWS
# ============================================================================

@require_http_methods(["GET"])
def get_store_whatsapp(request, store_id):
    try:
        store = Brand.objects.get(brand_id=store_id)
        phone = store.user_id.phone or getattr(settings, 'DEFAULT_SUPPORT_PHONE', '62812345678')
        phone = phone.replace('-', '').replace(' ', '')
        if not phone.startswith('62'):
            phone = '62' + phone.lstrip('0')
        
        return JsonResponse({
            'status': 'success',
            'phone': phone,
            'whatsapp_url': f'https://wa.me/{phone}',
            'message_template': f'Halo, saya tertarik dengan produk di toko Anda'
        })
    except Brand.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Toko tidak ditemukan'}, status=404)
    except:
        return JsonResponse({'status': 'success', 'phone': '62812345678', 'whatsapp_url': 'https://wa.me/62812345678'})


@require_http_methods(["POST"])
def submit_care_hub_inquiry(request):
    try:
        data = json.loads(request.body)
        topic = data.get('topic', 'general')
        message = data.get('message', '').strip()
        email = data.get('email', '').strip()
        
        if not message or len(message) < 10:
            return JsonResponse({'status': 'error', 'message': 'Pertanyaan minimal 10 karakter'}, status=400)
        
        try:
            from django.core.mail import send_mail
            send_mail(
                subject=f'[VOLTA Care Hub] {topic.upper()}',
                message=f'Email: {email}\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@volta.com'],
                fail_silently=True
            )
        except:
            pass
        
        return JsonResponse({
            'status': 'success',
            'message': 'Pertanyaan diterima! Tim support akan merespons dalam 1x24 jam.',
            'reference_code': f'CARE-{timezone.now().strftime("%Y%m%d%H%M%S")}'
        })
    except:
        return JsonResponse({'status': 'error', 'message': 'Error'}, status=500)


def verify_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user_id = request.session.get('pending_user_id')
        from django.utils import timezone
        from datetime import timedelta
        otp_obj = EmailOTP.objects.filter(
            user_id=user_id
        ).order_by('-created_at').first()
        if otp_obj:
            expired = timezone.now() > otp_obj.created_at + timedelta(minutes=5)
            if expired:
                messages.error(request, 'Kode OTP sudah kadaluarsa. Silakan login ulang.')
                return redirect('master_products:login')
            if otp_obj.otp_code == otp_input:
                user = User.objects.get(pk=user_id)
                auth_login(request, user)
                try:
                    del request.session['pending_user_id']
                except KeyError:
                    pass
                otp_obj.delete()
                return redirect('master_products:product_list')
            else:
                messages.error(request, 'Kode OTP salah. Silakan coba lagi.')
    return render(request, 'master_products/verify_otp.html')
