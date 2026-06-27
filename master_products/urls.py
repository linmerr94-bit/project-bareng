from django.urls import path
from . import views

app_name = 'master_products'

urlpatterns = [
    # ==================== ADMIN PANEL ====================
    path('brand-admin/', views.admin_panel_view, name='admin_panel'),
    path('brand-admin/verify-brand/<int:brand_id>/', views.admin_verify_brand, name='admin_verify_brand'),
    path('brand-admin/reject-brand/<int:brand_id>/', views.admin_reject_brand, name='admin_reject_brand'),
    
    # ==================== ADMIN PLATFORM ====================
    path('platform-admin/dashboard/', views.admin_platform_dashboard, name='admin_platform_dashboard'),
    path('market-admin/dashboard/', views.admin_platform_dashboard, name='market_admin_dashboard'),
    path('platform-admin/vendor-request/<int:request_id>/approve/', views.approve_vendor_request, name='approve_vendor_request'),
    path('platform-admin/vendor-request/<int:request_id>/reject/', views.reject_vendor_request, name='reject_vendor_request'),
    path('platform-admin/product/<int:product_id>/deactivate/', views.deactivate_product, name='deactivate_product'),
    path('platform-admin/user/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('platform-admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('platform-admin/approve-seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('platform-admin/reject-seller/<int:seller_id>/', views.reject_seller, name='reject_seller'),
    
    # ==================== AUTHENTICATION & DASHBOARD ====================
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    
    # ==================== CUSTOMER - PRODUCT CATALOG ====================
    path('', views.product_list, name='product_list'),
    path('shop/', views.shop, name='shop'),
    path('api/search/', views.product_list_ajax, name='product_list_ajax'),
    path('product/<int:product_id>/', views.product_detail_by_id, name='product_detail_by_id'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('store/<int:brand_id>/', views.store_detail, name='store_detail'),
    
    # ==================== CUSTOMER - SHOPPING CART ====================
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    
    # ==================== CUSTOMER - CHECKOUT & PAYMENT ====================
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('payment-gateway/<int:order_id>/', views.payment_gateway_view, name='payment_gateway_view'),
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice_view'),
    path('checkout/<int:order_id>/process/', views.process_payment_view, name='process_checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # ==================== USER PROFILE ====================
    path('profile/', views.user_profile_view, name='user_profile'),
    path('profile/enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('profile/disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    # ==================== SELLER - DASHBOARD & PRODUCT MANAGEMENT ====================
    path('toko/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/dashboard/', views.seller_dashboard),
    path('toko/chat/', views.brand_chat_inbox, name='brand_chat_inbox'),
    path('toko/chat/<int:room_id>/', views.brand_chat_detail, name='brand_chat_detail'),
    path('toko/produk/', views.seller_products, name='seller_products'),
    path('seller/products/', views.seller_products),
    path('toko/pesanan/', views.seller_orders, name='seller_orders'),
    path('seller/orders/', views.seller_orders),
    path('toko/order/<int:order_id>/', views.seller_order_detail, name='seller_order_detail'),
    path('seller/order/<int:order_id>/', views.seller_order_detail),
    path('toko/order/<int:order_id>/update/', views.seller_order_update, name='seller_order_update'),
    path('seller/order/<int:order_id>/update/', views.seller_order_update),
    path('toko/tambah-produk/', views.add_product_view, name='seller_add_product'),
    path('seller/add-product/', views.add_product_view),
    path('toko/edit-produk/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/edit-product/<int:product_id>/', views.edit_product),
    path('toko/hapus-produk/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/delete-product/<int:product_id>/', views.delete_product),
    
    # ==================== AUTHENTICATION ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_customer_view, name='register_customer'),
    path('toko/register/', views.register_vendor_view, name='register_vendor'),
    path('register-vendor/', views.register_vendor_view),
    path('toko/setup-account/<str:token>/', views.vendor_setup_account, name='vendor_setup_account'),
    
    # ==================== CART API ENDPOINTS ====================
    path('api/update-cart/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # ==================== CUSTOMER SERVICE API ====================
    path('api/store/<int:store_id>/whatsapp/', views.get_store_whatsapp, name='get_store_whatsapp'),
    path('api/care-hub/submit/', views.submit_care_hub_inquiry, name='submit_care_hub_inquiry'),
    path('chat/', views.chat_view, name='chat_view'),
    path('chat/<int:brand_id>/', views.chat_view, name='chat_room_detail'),
    path('api/chat/', views.chat_api, name='chat_api'),
    
    # ==================== USER PROFILE MANAGEMENT ====================
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/update-address/', views.update_address, name='update_address'),
    path('customer-orders/', views.order_list_view, name='customer_orders'),
]