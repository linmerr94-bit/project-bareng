from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


SELLER_ROLE_ALIASES = ('brand', 'penjual')


def role_required(*allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan role pengguna.
    
    Contoh penggunaan:
    @role_required('admin', 'brand')
    def my_view(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('master_products:login')
            
            if request.user.role not in allowed_roles:
                messages.error(
                    request,
                    '❌ Akses Ditolak! Anda tidak memiliki izin untuk mengakses halaman ini.'
                )
                return HttpResponseForbidden('Access Forbidden')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def seller_required(view_func):
    """
    Decorator untuk membatasi akses hanya ke penjual/toko yang disetujui.
    Memeriksa apakah user memiliki role penjual (brand/penjual) dan apakah toko sudah approved.

    Contoh penggunaan:
    @seller_required
    def seller_dashboard(request):
        pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('master_products:login')

        # If role isn't one of the known seller aliases, allow access still when
        # the user owns an approved toko. This covers cases where role value
        # may differ (e.g. 'vendor' or legacy values) but the user has a valid
        # approved Brand profile.
        if request.user.role not in SELLER_ROLE_ALIASES:
            current_toko_fallback = getattr(request.user, 'toko', None)
            if current_toko_fallback is None or not getattr(current_toko_fallback, 'is_approved', False):
                messages.error(
                    request,
                    '❌ Akses Ditolak! Hanya penjual yang dapat mengakses halaman ini.'
                )
                return HttpResponseForbidden('Access Forbidden')

        current_toko = getattr(request.user, 'toko', None)
        if current_toko is None:
            messages.error(
                request,
                '❌ Profil toko Anda belum terdaftar! Silakan hubungi admin atau daftar toko terlebih dahulu.'
            )
            return redirect('master_products:product_list')

        if not getattr(current_toko, 'is_approved', False):
            messages.warning(
                request,
                f'⏳ Toko Anda masih menunggu persetujuan dari admin. Status: {current_toko.get_status_display()}'
            )
            return redirect('master_products:product_list')

        return view_func(request, *args, **kwargs)

    return wrapper


def customer_required(view_func):
    """
    Decorator untuk membatasi akses hanya ke customer.
    
    Contoh penggunaan:
    @customer_required
    def customer_profile(request):
        pass
    """
    return role_required('customer')(view_func)


def admin_required(view_func):
    """
    Decorator untuk membatasi akses hanya ke admin.
    
    Contoh penggunaan:
    @admin_required
    def admin_dashboard(request):
        pass
    """
    return role_required('admin')(view_func)
