import base64
from decimal import Decimal

from django.test import TestCase

from cart.models import Cart, CartItem
from payments.services import MpesaSTKService
from products.models import Product, ProductCategory
from sales.models import SaleOrder


class MpesaSTKTests(TestCase):
    def test_build_password_uses_shortcode_passkey_and_timestamp(self):
        service = MpesaSTKService(shortcode='174379', passkey='testpasskey')
        timestamp = '20240606123456'

        expected = base64.b64encode(b'174379testpasskey20240606123456').decode('utf-8')

        self.assertEqual(service.build_password(timestamp), expected)

    def test_checkout_keeps_mpesa_order_pending_until_callback(self):
        category = ProductCategory.objects.create(name='Smartphones', slug='smartphones')
        product = Product.objects.create(
            name='Pixel 9',
            brand='Google',
            category=category,
            price=Decimal('12000.00'),
            stock_quantity=2,
            description='Flagship smartphone',
            device_type='mobile',
            condition='new',
        )

        cart = Cart.objects.create(session_key='test-cart')
        CartItem.objects.create(cart=cart, product=product, quantity=1)

        session = self.client.session
        session['cart_session'] = 'test-cart'
        session.save()

        response = self.client.post(
            '/cart/checkout/',
            {
                'customer_name': 'Alice',
                'customer_email': 'alice@example.com',
                'phone_number': '254712345678',
                'payment_method': 'mpesa',
            },
        )

        self.assertEqual(response.status_code, 200)
        order = SaleOrder.objects.get(customer_name='Alice')
        self.assertEqual(order.payment_method, 'mpesa')
        self.assertEqual(order.status, 'pending')
