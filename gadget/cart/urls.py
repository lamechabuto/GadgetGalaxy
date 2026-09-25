from django.urls import path

from .views import add_to_cart, cart_home, checkout_view

urlpatterns = [
    path('', cart_home, name='cart_home'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout_view, name='checkout_view'),
]
