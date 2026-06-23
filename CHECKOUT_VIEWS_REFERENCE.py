# CHECKOUT VIEW FUNCTIONS - master_products/views.py
# Tambahkan code ini ke dalam file master_products/views.py

# ==========================================================================================
# CHECKOUT VIEW - Menampilkan form checkout & memproses order creation
# ==========================================================================================

@login_required(login_url='master_products:login')
def checkout_view(request):
    """
    Menampilkan halaman checkout dengan:
    1. Ringkasan item belanjaan dari cart
    2. Form pengisian alamat pengiriman
    3. Form catatan pengiriman (opsional)
    4. Pilihan metode pembayaran dummy (Bank Transfer, E-Wallet, Credit Card, COD)
    5. Tombol "Bayar Sekarang" yang mengarah ke process_checkout
    
    GET Request:
    - Render template checkout.html dengan cart items dan summary
    
    POST Request:
    - Validasi data form
    - Buat Order record di database
    - Buat OrderItem untuk setiap item di cart
    - Clear cart items
    - Redirect ke payment success page
    
    Keamanan:
    - @login_required: User harus sudah login
    - Transaction atomicity: Semua atau tidak sama sekali
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
            'cart': cart,
            'cart_items': cart_items,
            'total_items': total_items,
            'total_price': total_price,
            'total_price_formatted': f"Rp{total_price:,.0f}",
            'user': request.user,
        }
        
        return render(request, 'master_products/checkout.html', context)
    
    if request.method == 'POST':
        # ==================== AMBIL DATA DARI FORM ====================
        receiver_name = request.POST.get('receiver_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_notes = request.POST.get('shipping_notes', '').strip()
        payment_method = request.POST.get('payment_method', '').strip()
        total_amount = request.POST.get('total_amount', '0').strip()
        
        # ==================== VALIDASI DATA ====================
        if not all([receiver_name, phone, shipping_address, payment_method]):
            messages.error(request, '❌ Nama penerima, nomor telepon, alamat, dan metode pembayaran harus diisi!')
            return redirect('master_products:checkout_view')
        
        # Validasi format telepon
        if not (phone.replace('-', '').replace('+', '').isdigit() and len(phone.replace('-', '').replace('+', '')) >= 10):
            messages.error(request, '❌ Nomor telepon tidak valid! Gunakan format: 08123456789')
            return redirect('master_products:checkout_view')
        
        if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
            messages.error(request, '❌ Metode pembayaran tidak valid!')
            return redirect('master_products:checkout_view')
        
        # ==================== MULAI TRANSACTION ====================
        try:
            with transaction.atomic():
                # ==================== 1. REFRESH CART ITEMS (UNTUK CEGAH RACE CONDITION) ====================
                cart_items = cart.items.all().select_related('product_id', 'product_id__brand_id')
                
                if not cart_items.exists():
                    messages.error(request, '❌ Keranjang Anda kosong!')
                    return redirect('master_products:product_list')
                
                # ==================== 2. VALIDASI STOK SEMUA PRODUK ====================
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
                    return redirect('master_products:cart_view')
                
                # ==================== 3. HITUNG TOTAL HARGA ====================
                total_amount_calculated = sum(float(item.price) * item.qty for item in cart_items)
                # Tambah ongkos kirim dummy (50.000)
                total_amount_calculated += 50000
                
                # ==================== 4. GET BRAND DARI CART ITEMS ====================
                # Catatan: Saat ini asumsi semua item dari 1 brand
                # Future: Bisa di-enhance untuk multi-brand cart
                first_brand = cart_items.first().product_id.brand_id
                
                # ==================== 5. GENERATE ORDER CODE ====================
                order_code = f"ORD-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
                
                # ==================== 6. CREATE ORDER ====================
                order = Order.objects.create(
                    user_id=request.user,
                    brand_id=first_brand,
                    order_code=order_code,
                    total_amount=total_amount_calculated,
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    receiver_name=receiver_name,
                    phone=phone,
                    status='pending',
                    payment_status='pending'
                )
                
                # ==================== 7. CREATE ORDER ITEMS & DECREMENT STOCK ====================
                for cart_item in cart_items:
                    # Create OrderItem
                    OrderItem.objects.create(
                        order_id=order,
                        product_id=cart_item.product_id,
                        price=cart_item.price,
                        qty=cart_item.qty
                    )
                    
                    # Decrement product stock
                    product = cart_item.product_id
                    product.stock -= cart_item.qty
                    product.save()
                
                # ==================== 8. DELETE CART ITEMS ====================
                cart_items.delete()
                
                # ==================== 9. SUCCESS MESSAGE & REDIRECT ====================
                messages.success(
                    request,
                    f'✅ Order berhasil dibuat! Kode Order: {order_code}'
                )
                
                # Redirect ke halaman pembayaran
                return redirect('master_products:process_checkout', order_id=order.order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat membuat order: {str(e)}')
            import traceback
            traceback.print_exc()
            return redirect('master_products:checkout_view')


# ==========================================================================================
# PROCESS CHECKOUT VIEW - Proses dummy payment dan redirect ke success page
# ==========================================================================================

@login_required(login_url='master_products:login')
def process_checkout(request, order_id):
    """
    Memproses dummy payment untuk order.
    
    Ini adalah FITUR DUMMY/SIMULASI untuk demonstrasi checkout flow.
    Tidak melakukan proses pembayaran sebenarnya.
    
    Fitur:
    1. GET request: Tampilkan halaman konfirmasi pembayaran
    2. POST request: 
       - Validasi user memiliki order tersebut
       - Update order status menjadi 'confirmed' (payment_status: 'paid')
       - Redirect ke halaman order success/receipt
    
    URL Parameters:
    - order_id: ID order yang ingin diproses
    
    Keamanan:
    - @login_required: User harus sudah login
    - Permission check: User hanya bisa proses order mereka sendiri
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
    
    # ==================== VALIDASI STATUS ORDER ====================
    if order.status != 'pending':
        messages.warning(request, f'⚠️ Order ini sudah diproses sebelumnya. Status: {order.status}')
        return redirect('master_products:order_detail', order_id=order_id)
    
    if request.method == 'GET':
        # ==================== GET ORDER ITEMS ====================
        order_items = order.items.all().select_related('product_id', 'product_id__brand_id')
        
        # ==================== BUILD CONTEXT UNTUK HALAMAN KONFIRMASI ====================
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
        
        return render(request, 'master_products/payment_confirmation.html', context)
    
    if request.method == 'POST':
        # ==================== DUMMY PAYMENT PROCESSING ====================
        # Ini adalah simulasi pembayaran. Di production, ini akan diintegrasikan dengan
        # payment gateway seperti Midtrans, Stripe, dll.
        
        try:
            with transaction.atomic():
                # ==================== UPDATE ORDER STATUS ====================
                order.status = 'confirmed'
                order.payment_status = 'paid'
                order.save()
                
                # ==================== SUCCESS MESSAGE ====================
                messages.success(
                    request,
                    f'✅ Pembayaran berhasil! Order Anda sedang diproses.\n'
                    f'Kode Order: {order.order_code}\n'
                    f'Total pembayaran: Rp{order.total_amount:,.0f}'
                )
                
                # Redirect ke halaman order detail
                return redirect('master_products:order_detail', order_id=order_id)
        
        except Exception as e:
            messages.error(request, f'❌ Terjadi kesalahan saat memproses pembayaran: {str(e)}')
            return redirect('master_products:process_checkout', order_id=order_id)


# ==========================================================================================
# ORDER DETAIL VIEW - Menampilkan detail order & status pembayaran
# ==========================================================================================

@login_required(login_url='master_products:login')
def order_detail(request, order_id):
    """
    Menampilkan halaman detail order dengan informasi lengkap.
    
    Fitur:
    1. Ringkasan order (order code, tanggal, status)
    2. List order items (produk, harga, jumlah)
    3. Informasi pengiriman (nama penerima, alamat, telepon)
    4. Status pembayaran & metode pembayaran
    5. Tombol tracking (untuk future development)
    
    Keamanan:
    - @login_required: User harus sudah login
    - Permission check: User hanya bisa lihat order mereka sendiri
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
        'order_status_display': dict(Order.ORDER_STATUS_CHOICES)[order.status],
        'payment_status_display': dict(Order.PAYMENT_STATUS_CHOICES)[order.payment_status],
        'receiver_name': order.receiver_name,
        'shipping_address': order.shipping_address,
        'phone': order.phone,
        'order_date': order.order_date.strftime('%d %b %Y, %H:%M'),
    }
    
    return render(request, 'master_products/order_detail.html', context)
