from django.db import models

from products.models import Product


class InventoryItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory_item')
    warehouse = models.CharField(max_length=100, default='Main Warehouse')
    reorder_level = models.PositiveIntegerField(default=5)
    last_counted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name} - {self.warehouse}'

    @property
    def available_stock(self):
        return self.product.stock_quantity


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.item.product.name} {self.movement_type} {self.quantity}'
