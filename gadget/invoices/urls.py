from django.urls import path

from .views import invoice_list, invoice_pdf

urlpatterns = [
    path('', invoice_list, name='invoice_list'),
    path('<int:invoice_id>/pdf/', invoice_pdf, name='invoice_pdf'),
]
