from django.apps import AppConfig


class MasterProductsConfig(AppConfig):
    """
    Konfigurasi aplikasi Master Products untuk platform B2B2C VOLTA.
    App ini mengelola katalog produk, cart, orders, dan reviews.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'master_products'
    verbose_name = 'Product Catalog & Commerce'
