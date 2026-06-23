"""
VOLTA Platform B2B2C - Models Quick Reference Guide
====================================================

Panduan cepat untuk menggunakan 9 models yang telah dibuat.
"""

# ============================================================================
# 1. USER MODEL - AUTHENTICATION & ROLES
# ============================================================================

from users.models import User

# Create Regular User
user = User.objects.create_user(
    username='john_customer',
    email='john@example.com',
    password='securepass123',
    full_name='John Doe',
    phone='081234567890',
    role='customer'
)

# Create Brand User
brand_user = User.objects.create_user(
    username='sony_brand',
    email='sony@example.com',
    password='brandpass123',
    full_name='Sony Indonesia',
    phone='081987654321',
    role='brand'
)

# Create Admin User
admin = User.objects.create_superuser(
    username='admin',
    email='admin@volta.local',
    password='adminpass123',
    full_name='Administrator',
    role='admin'
)

# Query Users by Role
customers = User.objects.filter(role='customer')
brands = User.objects.filter(role='brand')
admins = User.objects.filter(role='admin', is_superuser=True)

# Update User
user.full_name = 'John Doe Updated'
user.phone = '082345678901'
user.save()


# ============================================================================
# 2. BRANDS MODEL - VENDOR MANAGEMENT
# ============================================================================

from master_products.models import Brands

# Create Brand (linked to brand_user)
sony_brand = Brands.objects.create(
    user_id=brand_user,
    brand_name='Sony Electronics Indonesia',
    description='Official distributor of Sony electronics',
    status='pending',  # Will be approved by admin
    # logo field untuk upload file
)

# Query Brands by Status
pending_brands = Brands.objects.filter(status='pending')
approved_brands = Brands.objects.filter(status='approved')

# Approve Brand by Admin
sony_brand.status = 'approved'
sony_brand.approved_at = timezone.now()
sony_brand.approved_by = admin  # Set admin yang approve
sony_brand.save()

# Get brand from user
user_brand = brand_user.brand_profile  # OneToOne reverse access


# ============================================================================
# 3. CATEGORIES MODEL - PRODUCT CLASSIFICATION
# ============================================================================

from master_products.models import Categories

# Create Categories
electronics = Categories.objects.create(
    category_name='Electronics',
    description='Electronic devices and gadgets'
)

smartphones = Categories.objects.create(
    category_name='Smartphones',
    description='Mobile phones and smartphones'
)

televisions = Categories.objects.create(
    category_name='Televisions',
    description='TV sets and displays'
)

# Query Categories
all_categories = Categories.objects.all()
electronics_cat = Categories.objects.get(category_name='Smartphones')


# ============================================================================
# 4. PRODUCTS MODEL - CATALOG MANAGEMENT
# ============================================================================

from master_products.models import Products
from django.utils.text import slugify

# Create Product
iphone14 = Products.objects.create(
    brand_id=sony_brand,
    category_id=smartphones,
    product_name='Sony Xperia Pro-I',
    slug=slugify('Sony Xperia Pro-I'),  # Auto slugify
    description='Flagship smartphone with advanced camera',
    price='12999999.00',  # Decimal(12,2)
    stock=150,
    image='products/sony_xperia.jpg',  # Upload image
    is_active=True
)

# Query Products
active_products = Products.objects.filter(is_active=True)
sony_products = Products.objects.filter(brand_id=sony_brand)
smartphones_list = Products.objects.filter(category_id=smartphones)

# Get product by slug
product = Products.objects.get(slug='sony-xperia-pro-i')

# Update Product Stock
iphone14.stock -= 10
iphone14.save()


# ============================================================================
# 5. CARTS MODEL - SHOPPING CART MANAGEMENT
# ============================================================================

from master_products.models import Carts

# Get or Create Cart for User (auto created when user created)
cart = user.cart  # OneToOne reverse access
# atau
cart, created = Carts.objects.get_or_create(user_id=user)

# Query carts
active_carts = Carts.objects.all()


# ============================================================================
# 6. CART ITEMS MODEL - ITEMS IN SHOPPING CART
# ============================================================================

from master_products.models import CartItems

# Add Item to Cart
cart_item = CartItems.objects.create(
    cart_id=cart,
    product_id=iphone14,
    qty=2,
    price=iphone14.price  # Capture price at time of adding
)

# Add Another Product
tv_product = Products.objects.create(
    brand_id=sony_brand,
    category_id=televisions,
    product_name='Sony Bravia 55"',
    slug=slugify('Sony Bravia 55'),
    description='4K Smart TV',
    price='8999999.00',
    stock=50,
    is_active=True
)

tv_cart_item = CartItems.objects.create(
    cart_id=cart,
    product_id=tv_product,
    qty=1,
    price=tv_product.price
)

# Get items in cart
cart_items = cart.items.all()

# Update Cart Item Quantity
cart_item.qty = 3
cart_item.save()

# Remove Item from Cart
cart_item.delete()

# Clear Cart
cart.items.all().delete()


# ============================================================================
# 7. ORDERS MODEL - ORDER MANAGEMENT
# ============================================================================

from master_products.models import Orders
from datetime import datetime
import uuid

# Create Order (from checkout/cart)
order = Orders.objects.create(
    user_id=user,
    brand_id=sony_brand,
    order_code=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",  # Generate unique code
    status='pending',
    total_amount='13999998.00',  # Total dari cart items
    payment_method='bank_transfer',
    payment_status='pending',
    shipping_address='Jl. Merdeka No. 123, Jakarta, 12000',
    receiver_name='John Doe',
    phone='081234567890'
)

# Query Orders
user_orders = Orders.objects.filter(user_id=user)
pending_orders = Orders.objects.filter(status='pending')
paid_orders = Orders.objects.filter(payment_status='paid')
brand_orders = Orders.objects.filter(brand_id=sony_brand)

# Update Order Status
order.status = 'confirmed'
order.save()

# Mark as Paid
order.payment_status = 'paid'
order.status = 'processing'
order.save()

# Track Order
order.status = 'shipped'
order.save()

order.status = 'delivered'
order.save()


# ============================================================================
# 8. ORDER ITEMS MODEL - ITEMS IN ORDER
# ============================================================================

from master_products.models import OrderItems

# Add items to order
order_item1 = OrderItems.objects.create(
    order_id=order,
    product_id=iphone14,
    price='12999999.00',  # Price at time of order
    qty=1
)

order_item2 = OrderItems.objects.create(
    order_id=order,
    product_id=tv_product,
    price='8999999.00',
    qty=1
)

# Get order items
items = order.items.all()

# Calculate order totals
total = sum(item.price * item.qty for item in items)


# ============================================================================
# 9. REVIEWS MODEL - PRODUCT RATINGS
# ============================================================================

from master_products.models import Reviews

# Add Review (after order delivered)
review = Reviews.objects.create(
    product_id=iphone14,
    user_id=user,
    rating=5,  # 1-5 stars
    comment='Excellent smartphone! Great camera and performance.'
)

# Query Reviews
product_reviews = Reviews.objects.filter(product_id=iphone14)
user_reviews = Reviews.objects.filter(user_id=user)
top_reviews = Reviews.objects.filter(rating=5)

# Calculate average rating
from django.db.models import Avg
avg_rating = Reviews.objects.filter(product_id=iphone14).aggregate(
    avg=Avg('rating')
)['avg']

# Get review count
review_count = Reviews.objects.filter(product_id=iphone14).count()


# ============================================================================
# ADVANCED QUERIES & OPERATIONS
# ============================================================================

# 1. USER AUTHENTICATION
from django.contrib.auth import authenticate, login
user_auth = authenticate(username='john_customer', password='securepass123')

# 2. CART TOTAL CALCULATION
from django.db.models import F, DecimalField, Sum, ExpressionWrapper
cart_total = CartItems.objects.filter(
    cart_id=cart
).aggregate(
    total=Sum(
        ExpressionWrapper(F('qty') * F('price'), output_field=DecimalField())
    )
)['total']

# 3. PRODUCT AVAILABILITY CHECK
in_stock = Products.objects.filter(stock__gt=0, is_active=True)
out_of_stock = Products.objects.filter(stock=0)

# 4. ORDER STATISTICS
from django.db.models import Count, Sum
monthly_orders = Orders.objects.filter(
    created_at__year=2026,
    created_at__month=6
).count()

total_revenue = Orders.objects.filter(
    payment_status='paid'
).aggregate(Sum('total_amount'))['total_amount__sum']

# 5. BRAND PERFORMANCE
brand_stats = Orders.objects.filter(brand_id=sony_brand).aggregate(
    total_orders=Count('order_id'),
    total_revenue=Sum('total_amount')
)

# 6. PRODUCT POPULARITY
from django.db.models import Count
popular_products = OrderItems.objects.values('product_id').annotate(
    total_sold=Sum('qty')
).order_by('-total_sold')[:10]

# 7. FILTER & SEARCH
searched = Products.objects.filter(
    product_name__icontains='Sony'
) | Products.objects.filter(
    description__icontains='camera'
)

# 8. PAGINATION
from django.core.paginator import Paginator
products = Products.objects.all()
paginator = Paginator(products, 10)  # 10 per page
page_1 = paginator.get_page(1)


# ============================================================================
# DJANGO SHELL EXAMPLES
# ============================================================================

"""
# Run Django Shell
python manage.py shell

# Import Models
from users.models import User
from master_products.models import *

# Create User
user = User.objects.create_user(username='test', email='test@test.com', password='pass')

# Create Brand
brand = Brands.objects.create(user_id=user, brand_name='Test Brand')

# Create Category
cat = Categories.objects.create(category_name='Test Category')

# Create Product
prod = Products.objects.create(brand_id=brand, category_id=cat, product_name='Test', slug='test', price=100)

# Create Cart
cart = user.cart

# Add to Cart
CartItems.objects.create(cart_id=cart, product_id=prod, qty=1, price=100)

# Create Order
order = Orders.objects.create(user_id=user, brand_id=brand, order_code='ORD001', status='pending', total_amount=100)

# Add to Order
OrderItems.objects.create(order_id=order, product_id=prod, qty=1, price=100)

# Add Review
Reviews.objects.create(product_id=prod, user_id=user, rating=5, comment='Great!')
"""


# ============================================================================
# COMMON PATTERNS & BEST PRACTICES
# ============================================================================

"""
1. TRANSACTION HANDLING
from django.db import transaction

@transaction.atomic
def create_order_from_cart(user):
    cart = user.cart
    items = cart.items.all()
    
    # Create order
    order = Orders.objects.create(...)
    
    # Copy cart items to order items
    for item in items:
        OrderItems.objects.create(...)
    
    # Clear cart
    items.delete()
    
    return order

2. SIGNAL HANDLING
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Carts.objects.create(user_id=instance)

3. MODEL METHODS
class Products(models.Model):
    def is_available(self):
        return self.stock > 0 and self.is_active
    
    def get_discount_percentage(self, base_price):
        if base_price > 0:
            return int(((base_price - self.price) / base_price) * 100)
        return 0

4. QUERYSET OPTIMIZATION
from django.db.models import Prefetch, Q
products = Products.objects.select_related(
    'brand_id', 'category_id'
).prefetch_related(
    'reviews'
).filter(is_active=True)

5. BULK OPERATIONS
CartItems.objects.bulk_create([
    CartItems(cart_id=cart, product_id=prod1, qty=1, price=100),
    CartItems(cart_id=cart, product_id=prod2, qty=2, price=200),
])

6. ADMIN ACTIONS
def approve_brands(modeladmin, request, queryset):
    queryset.update(status='approved', approved_by=request.user)

approve_brands.short_description = "Approve selected brands"
"""


# ============================================================================
# VALIDATION & ERROR HANDLING
# ============================================================================

"""
# Check duplicate order code
if Orders.objects.filter(order_code=order_code).exists():
    raise ValidationError("Order code already exists")

# Validate stock
if product.stock < quantity:
    raise ValidationError("Insufficient stock")

# Validate unique constraint
try:
    review = Reviews.objects.create(product_id=product, user_id=user, rating=5)
except IntegrityError:
    raise ValidationError("User already reviewed this product")

# Get or create pattern
cart, created = Carts.objects.get_or_create(user_id=user)

# Conditional updates
Products.objects.filter(stock__lt=10).update(is_active=False)
"""

print("✅ VOLTA Models Quick Reference - Ready to Use!")
