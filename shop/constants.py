# Shop Constants
# These values are used throughout the app to maintain consistency

# ==========================================
# CART & ORDER DEFAULTS
# ==========================================
DEFAULT_QUANTITY = 1
MAX_QUANTITY = 100
MIN_QUANTITY = 1

# ==========================================
# PAGE SIZES & LIMITS
# ==========================================
FEATURED_PRODUCTS_COUNT = 6
TESTIMONIALS_COUNT = 4
REVIEWS_PER_PAGE = 10
PRODUCTS_PER_PAGE = 20

# ==========================================
# SESSION KEYS
# ==========================================
CART_SESSION_KEY = 'shopping_cart'

# ==========================================
# ORDER STATUSES
# ==========================================
ORDER_PENDING = 'pending'
ORDER_CONFIRMED = 'confirmed'
ORDER_SHIPPED = 'shipped'
ORDER_DELIVERED = 'delivered'
ORDER_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = [
    (ORDER_PENDING, 'Pending'),
    (ORDER_CONFIRMED, 'Confirmed'),
    (ORDER_SHIPPED, 'Shipped'),
    (ORDER_DELIVERED, 'Delivered'),
    (ORDER_CANCELLED, 'Cancelled'),
]

# ==========================================
# PRODUCT BADGES
# ==========================================
BADGE_NONE = ''
BADGE_NEW = 'new'
BADGE_SALE = 'sale'
BADGE_BEST_SELLER = 'best'

BADGE_CHOICES = [
    (BADGE_NONE, 'None'),
    (BADGE_NEW, 'New'),
    (BADGE_SALE, 'Sale'),
    (BADGE_BEST_SELLER, 'Best Seller'),
]

# ==========================================
# VALIDATION LIMITS
# ==========================================
MAX_PRODUCT_NAME_LENGTH = 160
MAX_CATEGORY_NAME_LENGTH = 120
MAX_PRODUCT_DESCRIPTION_LENGTH = 10000
MIN_PRICE = 0
MAX_PRICE = 99999999  # Realistic upper bound

# ==========================================
# ERROR MESSAGES
# ==========================================
ERROR_PRODUCT_NOT_FOUND = 'Product not found'
ERROR_CATEGORY_NOT_FOUND = 'Category not found'
ERROR_INVALID_QUANTITY = 'Invalid quantity. Please enter a number between 1 and 100'
ERROR_CART_EMPTY = 'Your cart is empty'
ERROR_INSUFFICIENT_STOCK = 'Not enough stock available'

# ==========================================
# SUCCESS MESSAGES
# ==========================================
SUCCESS_PRODUCT_ADDED = 'Product added to cart successfully'
SUCCESS_PRODUCT_REMOVED = 'Product removed from cart'
SUCCESS_ORDER_PLACED = 'Order placed successfully'
SUCCESS_ACCOUNT_CREATED = 'Account created successfully 🎉'

# ==========================================
# PAGINATION
# ==========================================
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ==========================================
# API LIMITS
# ==========================================
API_RATE_LIMIT_ANON = '100/hour'
API_RATE_LIMIT_USER = '1000/hour'

# ==========================================
# TIMEOUT VALUES (in seconds)
# ==========================================
CACHE_TIMEOUT_PRODUCTS = 300  # 5 minutes
CACHE_TIMEOUT_CATEGORIES = 3600  # 1 hour
CACHE_TIMEOUT_FEATURED = 600  # 10 minutes
