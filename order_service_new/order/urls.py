from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PublicOrderView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('public/order/<int:order_id>/', PublicOrderView.as_view(), name='public-order-detail'),
    path('', include(router.urls)),
]
