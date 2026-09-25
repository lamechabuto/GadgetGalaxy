from decimal import Decimal

from django.test import TestCase

from cart.models import Cart
from products.models import Product, ProductCategory


class CartCheckoutTests(TestCase):
    def test_cart_checkout_creates_order_and_invoice_and_reduces_stock(self):
        category = ProductCategory.objects.create(name='Laptops', slug='laptops')
        product = Product.objects.create(
            name='ThinkPad X1',
            brand='Lenovo',
            category=category,
            price=Decimal('1299.00'),
            stock_quantity=5,
            description='Business laptop',
            device_type='laptop',
            condition='new',
        )

        cart = Cart.objects.create(session_key='checkout-session')
        cart.add_item(product, quantity=2)

        order = cart.checkout('Dana', 'dana@example.com', 'lipa_pole_pole')
        product.refresh_from_db()

        self.assertEqual(order.total_amount, Decimal('2598.00'))
        self.assertEqual(order.payment_method, 'lipa_pole_pole')
        self.assertEqual(product.stock_quantity, 3)
        self.assertTrue(hasattr(order, 'invoice'))
        self.assertEqual(order.invoice.total_amount, Decimal('2598.00'))
