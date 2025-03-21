from django.urls import path
from .views import *

urlpatterns = [
    path('carts/add-to-cart', add_to_cart),
    path('carts/remove-from-cart/<int:cart_id>', remove_from_cart),
    path('carts/cart-items', get_cart_items),
    path('carts/edit/<int:cart_id>', edit_cart),
    path('carts/total-price', calculate_total_price),
    path('carts/filter-by-time', filter_cart_by_time),
    path('carts/check-out', check_out),
]
