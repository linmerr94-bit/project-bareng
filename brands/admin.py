from django.contrib import admin
from .models import BrandProfile


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    """Admin interface untuk BrandProfile"""
    
    list_display = ('brand_name', 'user', 'status', 'rating', 'created_at')
    list_filter = ('status', 'created_at', 'rating')
    search_fields = ('brand_name', 'nib_or_ktp', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Brand', {
            'fields': ('user', 'brand_name', 'nib_or_ktp')
        }),
        ('Status & Rating', {
            'fields': ('status', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Cegah perubahan user setelah brand dibuat"""
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields
