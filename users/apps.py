from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Konfigurasi aplikasi Users untuk platform B2B2C VOLTA.
    App ini mengelola custom User model dengan role-based access control.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
