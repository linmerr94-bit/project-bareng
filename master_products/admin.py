from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Brand, Category, Product, 
    Cart, CartItem, 
    Order, OrderItem, 
    Review, VendorRequest
)


# ============================================================================
# BRANDS ADMIN
# ============================================================================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin interface untuk Brand model"""
    
    list_display = (
        'brand_id', 'brand_name', 'user_id', 'nib_or_ktp', 'rating', 'status_badge', 'created_at'
    )
    list_filter = ('status', 'created_at', 'approved_at')
    search_fields = ('brand_name', 'user_id__username', 'user_id__email')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'rating')
    
    fieldsets = (
        (_('Brand Information'), {
            'fields': ('user_id', 'brand_name', 'logo', 'description', 'nib_or_ktp')
        }),
        (_('Performance Metrics'), {
            'fields': ('rating',)
        }),
        (_('Approval Status'), {
            'fields': ('status', 'approved_at', 'approved_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def status_badge(self, obj):
        """Display status dengan warna"""
        colors = {
            'pending': '#FFA500',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')


# ============================================================================
# CATEGORIES ADMIN
# ============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface untuk Category model"""
    
    list_display = ('category_id', 'category_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('category_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Category Information'), {
            'fields': ('category_name', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('category_name',)


# ============================================================================
# PRODUCTS ADMIN
# ============================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface untuk Product model"""
    
    list_display = (
        'product_id', 'product_name', 'get_brand_name', 'get_category_name',
        'price', 'stock', 'is_active_badge'
    )
    list_filter = ('is_active', 'brand_id', 'category_id', 'created_at')
    search_fields = ('product_name', 'slug', 'description', 'brand_id__brand_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product_name', 'slug', 'description', 'image')
        }),
        (_('Classification'), {
            'fields': ('brand_id', 'category_id')
        }),
        (_('Pricing & Stock'), {
            'fields': ('price', 'stock')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def get_brand_name(self, obj):
        """Display brand name"""
        return obj.brand_id.brand_name if obj.brand_id else '-'
    get_brand_name.short_description = _('Brand')
    
    def get_category_name(self, obj):
        """Display category name"""
        return obj.category_id.category_name if obj.category_id else '-'
    get_category_name.short_description = _('Category')
    
    def is_active_badge(self, obj):
        """Display active status dengan badge"""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Inactive</span>'
        )
    is_active_badge.short_description = _('Status')


# ============================================================================
# CARTS ADMIN
# ============================================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface untuk Cart model"""
    
    list_display = ('cart_id', 'user_id', 'item_count')
    list_filter = ('user_id__role',)
    search_fields = ('user_id__username', 'user_id__email')
    readonly_fields = ('cart_id', 'user_id')
    
    def item_count(self, obj):
        """Display jumlah item dalam cart"""
        return obj.items.count()
    item_count.short_description = _('Items')


# ============================================================================
# CART ITEM ADMIN (INLINE)
# ============================================================================

class CartItemInline(admin.TabularInline):
    """Inline admin untuk CartItem dalam Cart"""
    model = CartItem
    extra = 0
    readonly_fields = ('product_id', 'price', 'created_at', 'updated_at')
    fields = ('product_id', 'qty', 'price', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface untuk CartItem model"""
    
    list_display = ('cart_item_id', 'cart_id', 'product_id', 'qty', 'price')
    list_filter = ('cart_id', 'product_id', 'created_at')
    search_fields = ('cart_id__user_id__username', 'product_id__product_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Cart & Product'), {
            'fields': ('cart_id', 'product_id')
        }),
        (_('Quantity & Price'), {
            'fields': ('qty', 'price')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ORDER MODEL
# ============================================================================

class OrderItemInline(admin.TabularInline):
    """Inline admin untuk OrderItem dalam Order"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_id', 'price', 'qty', 'created_at')
    fields = ('product_id', 'qty', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface untuk Order model"""
    
    list_display = (
        'order_id', 'order_code', 'user_id', 'brand_id',
        'status_badge', 'payment_status_badge', 'total_amount'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_code', 'user_id__username', 'receiver_name')
    readonly_fields = ('order_code', 'created_at', 'updated_at', 'order_date')
    inlines = [OrderItemInline]
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_code', 'user_id', 'brand_id', 'order_date')
        }),
        (_('Status'), {
            'fields': ('status', 'payment_method', 'payment_status')
        }),
        (_('Pricing'), {
            'fields': ('total_amount',)
        }),
        (_('Shipping Information'), {
            'fields': ('shipping_address', 'receiver_name', 'phone')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def status_badge(self, obj):
        """Display order status dengan warna"""
        colors = {
            'pending': '#FFA500',
            'confirmed': '#0275d8',
            'processing': '#17a2b8',
            'shipped': '#20c997',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'returned': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Order Status')
    
    def payment_status_badge(self, obj):
        """Display payment status dengan warna"""
        colors = {
            'pending': '#FFA500',
            'paid': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = _('Payment Status')


# ============================================================================
# ORDER ITEM ADMIN
# ============================================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface untuk OrderItem model"""
    
    list_display = ('order_item_id', 'order_id', 'product_id', 'qty', 'price')
    list_filter = ('order_id', 'product_id', 'created_at')
    search_fields = ('order_id__order_code', 'product_id__product_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Order & Product'), {
            'fields': ('order_id', 'product_id')
        }),
        (_('Quantity & Price'), {
            'fields': ('qty', 'price')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# REVIEW ADMIN
# ============================================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface untuk Review model"""
    
    list_display = (
        'review_id', 'product_id', 'user_id',
        'rating_stars', 'created_at'
    )
    list_filter = ('rating', 'product_id', 'user_id', 'created_at')
    search_fields = ('product_id__product_name', 'user_id__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('product_id', 'user_id', 'rating', 'comment')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def rating_stars(self, obj):
        """Display rating dengan stars"""
        stars = '⭐' * obj.rating
        return format_html(
            '<span style="color: #FFB81C;">{}</span>',
            stars
        )
    rating_stars.short_description = _('Rating')


# ============================================================================
# VENDOR REQUEST ADMIN
# ============================================================================

@admin.register(VendorRequest)
class VendorRequestAdmin(admin.ModelAdmin):
    """Admin interface untuk VendorRequest model"""
    
    list_display = (
        'vendor_name', 'nib', 'status_badge', 'category', 'created_at'
    )
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('vendor_name', 'nib', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Vendor Information'), {
            'fields': ('user', 'vendor_name', 'nib', 'category')
        }),
        (_('Business Details'), {
            'fields': ('address', 'description')
        }),
        (_('Request Status'), {
            'fields': ('status', 'admin_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def status_badge(self, obj):
        """Display status dengan warna"""
        colors = {
            'Pending': '#FFA500',
            'Approved': '#28a745',
            'Rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
