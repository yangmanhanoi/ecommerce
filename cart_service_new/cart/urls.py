from django.urls import path
from .views import *

urlpatterns = [
    path('/add-to-cart', add_to_cart),
    path('/remove-from-cart/<int:cart_id>', remove_from_cart),
    path('/cart-items', get_cart_items),
    path('/edit/<int:cart_id>', edit_cart),
    path('/total-price', calculate_total_price),
    path('/filter-by-time', filter_cart_by_time),
    path('/check-out', check_out),
    path('/test', test_access),
    path('view/', get_cart_items, name='cart_view'), 
]
