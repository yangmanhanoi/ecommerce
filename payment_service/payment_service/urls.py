"""
URL configuration for payment_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from payment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('paypal-ipn/', include('paypal.standard.ipn.urls')),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_failed, name='payment_failed'),
    path('paypal/<int:shipment_id>', views.payment, name='payment')
]
