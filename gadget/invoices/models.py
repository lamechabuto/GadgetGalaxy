from decimal import Decimal

from django.db import models

from sales.models import SaleOrder


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(SaleOrder, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.invoice_number

    @classmethod
    def create_from_order(cls, order):
        invoice_number = f'INV-{order.pk:05d}'
        return cls.objects.create(
            order=order,
            invoice_number=invoice_number,
            total_amount=order.total_amount,
            status='paid' if order.status == 'paid' else 'draft',
        )
