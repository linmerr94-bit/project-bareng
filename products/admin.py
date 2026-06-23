from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface untuk Category"""
    
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Kategori', {
            'fields': ('name', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface untuk Product"""
    
    list_display = ('name', 'sku', 'brand', 'category', 'price_b2c', 
                    'price_b2b', 'moq_b2b', 'stock', 'is_active', 'rating')
    list_filter = ('is_active', 'category', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'brand__brand_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Produk', {
            'fields': ('brand', 'category', 'name', 'sku', 'description')
        }),
        ('Harga (REQ-F009)', {
            'fields': ('price_b2c', 'price_b2b'),
            'description': 'Harga eceran (B2C) dan harga grosir (B2B)'
        }),
        ('Pesanan Grosir (REQ-F010)', {
            'fields': ('moq_b2b',),
            'description': 'Minimum Order Quantity untuk pesanan dengan harga B2B'
        }),
        ('Inventori & Status (REQ-F010)', {
            'fields': ('stock', 'is_active', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Cegah perubahan brand dan SKU setelah produk dibuat"""
        if obj:
            return self.readonly_fields + ('brand', 'sku')
        return self.readonly_fields
