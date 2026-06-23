from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


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
                    f'❌ Akses Ditolak! Anda tidak memiliki izin untuk mengakses halaman ini.'
                )
                return HttpResponseForbidden('Access Forbidden')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def seller_required(view_func):
    """
    Decorator untuk membatasi akses hanya ke penjual (brand/vendor).
    Singkatan dari @role_required('brand')
    
    Contoh penggunaan:
    @seller_required
    def seller_dashboard(request):
        pass
    """
    return role_required('brand')(view_func)


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
