from django.urls import path

from .views import mpesa_callback, mpesa_timeout

urlpatterns = [
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('mpesa/timeout/', mpesa_timeout, name='mpesa_timeout'),
]
