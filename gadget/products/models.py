from decimal import Decimal

from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('mobile', 'Mobile'),
        ('laptop', 'Laptop'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('refurbished', 'Refurbished'),
        ('used', 'Used'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.brand} {self.name}'

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/default-product.png'

    def reduce_stock(self, quantity):
        if quantity < 0:
            raise ValueError('Quantity cannot be negative.')
        if quantity > self.stock_quantity:
            raise ValueError('Not enough stock available.')
        self.stock_quantity -= quantity
        self.save(update_fields=['stock_quantity', 'updated_at'])
        ProductInventoryLog.objects.create(
            product=self,
            change_quantity=-quantity,
            reason='sale',
        )
        return self.stock_quantity

    def add_stock(self, quantity, reason='restock'):
        if quantity < 0:
            raise ValueError('Quantity cannot be negative.')
        self.stock_quantity += quantity
        self.save(update_fields=['stock_quantity', 'updated_at'])
        ProductInventoryLog.objects.create(
            product=self,
            change_quantity=quantity,
            reason=reason,
        )
        return self.stock_quantity

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def supports_lipa_pole_pole(self):
        return self.device_type == 'mobile'

    @property
    def lipa_pole_pole_deposit(self):
        if not self.supports_lipa_pole_pole:
            return Decimal('0.00')
        return (self.price * Decimal('0.30')).quantize(Decimal('0.01'))

    @property
    def lipa_pole_pole_daily_payment(self):
        if not self.supports_lipa_pole_pole:
            return Decimal('0.00')
        remaining_after_deposit = self.price - self.lipa_pole_pole_deposit
        return (remaining_after_deposit / Decimal('360')).quantize(Decimal('0.01'))


class ProductInventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    change_quantity = models.IntegerField()
    reason = models.CharField(max_length=100, default='inventory_update')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name}: {self.change_quantity}'
