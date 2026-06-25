from django.contrib import admin
from .models import VendorRequest


@admin.register(VendorRequest)
class VendorRequestAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'email', 'category', 'status')
    list_filter = ('status', 'category')
    search_fields = ('vendor_name', 'email')
    list_editable = ('status',)
