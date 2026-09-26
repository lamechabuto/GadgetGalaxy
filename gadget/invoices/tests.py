from decimal import Decimal
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from pypdf import PdfReader

from cart.models import Cart
from invoices.models import Invoice
from products.models import Product, ProductCategory


class InvoicePdfTests(TestCase):
    def test_invoice_pdf_endpoint_returns_a_pdf(self):
        category = ProductCategory.objects.create(name='Accessories', slug='accessories')
        product = Product.objects.create(
            name='Wireless Mouse',
            brand='Logitech',
            category=category,
            price=Decimal('49.99'),
            stock_quantity=8,
            description='Compact wireless mouse',
            device_type='accessory',
            condition='new',
        )

        cart = Cart.objects.create(session_key='invoice-pdf-session')
        cart.add_item(product, quantity=2)
        order = cart.checkout('Ada Lovelace', 'ada@example.com', 'cash')

        invoice = Invoice.objects.get(order=order)
        response = self.client.get(reverse('invoice_pdf', args=[invoice.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('filename="INV-', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

        reader = PdfReader(BytesIO(response.content))
        pages_text = ''
        for page in reader.pages:
            pages_text += page.extract_text() or ''

        self.assertIn('Ksh.', pages_text)
        self.assertNotIn('USD', pages_text)
        self.assertNotIn('$', pages_text)
