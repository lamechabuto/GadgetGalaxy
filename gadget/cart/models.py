from decimal import Decimal

from django.db import models

from products.models import Product
from sales.models import SaleOrder, SaleOrderItem


class Cart(models.Model):
    session_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart {self.session_key}'

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0.00'))

    def add_item(self, product, quantity=1):
        item, created = self.items.get_or_create(product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity'])
        return item

    def clear(self):
        self.items.all().delete()

    def checkout(self, customer_name, customer_email='', payment_method='cash'):
        if not self.items.exists():
            raise ValueError('Cart is empty.')

        order = SaleOrder.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            status='pending',
            payment_method=payment_method,
        )

        for item in self.items.select_related('product'):
            SaleOrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )

        order.mark_paid()
        from invoices.models import Invoice
        Invoice.create_from_order(order)
        self.clear()
        return order


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
