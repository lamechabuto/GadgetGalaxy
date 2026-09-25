from decimal import Decimal

from django.db import models

from sales.models import SaleOrder


class MpesaTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(SaleOrder, on_delete=models.CASCADE, related_name='mpesa_transaction')
    merchant_request_id = models.CharField(max_length=100, blank=True, default='')
    checkout_request_id = models.CharField(max_length=100, blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    phone_number = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_code = models.CharField(max_length=20, blank=True, default='')
    response_description = models.CharField(max_length=255, blank=True, default='')
    callback_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'M-Pesa {self.order_id} - {self.status}'

    def mark_success(self):
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])
        self.order.status = 'paid'
        self.order.save(update_fields=['status', 'updated_at'])

    def mark_failed(self):
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])
        self.order.status = 'pending'
        self.order.save(update_fields=['status', 'updated_at'])
