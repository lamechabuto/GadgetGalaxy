from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from products.models import Product, ProductCategory
from sales.models import SaleOrder, SaleOrderItem


class ProductAndSalesTests(TestCase):
    def test_product_stock_reduces_and_sale_total_is_calculated(self):
        category = ProductCategory.objects.create(name='Smartphones', slug='smartphones')
        product = Product.objects.create(
            name='Pixel 9',
            brand='Google',
            category=category,
            price=Decimal('799.00'),
            stock_quantity=10,
            description='Flagship smartphone',
            device_type='mobile',
            condition='new',
        )

        order = SaleOrder.objects.create(customer_name='Alice', status='paid')
        SaleOrderItem.objects.create(order=order, product=product, quantity=2, unit_price=product.price)

        product.reduce_stock(2)
        product.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(product.stock_quantity, 8)
        self.assertEqual(order.total_amount, Decimal('1598.00'))

    def test_product_list_filters_by_category(self):
        smartphones = ProductCategory.objects.create(name='Smartphones', slug='smartphones')
        laptops = ProductCategory.objects.create(name='Laptops', slug='laptops')

        Product.objects.create(
            name='Pixel 9',
            brand='Google',
            category=smartphones,
            price=Decimal('799.00'),
            stock_quantity=5,
            description='Flagship smartphone',
            device_type='mobile',
            condition='new',
        )
        Product.objects.create(
            name='MacBook Pro',
            brand='Apple',
            category=laptops,
            price=Decimal('1999.00'),
            stock_quantity=3,
            description='Laptop computer',
            device_type='laptop',
            condition='new',
        )

        response = self.client.get('/products/?category=smartphones')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pixel 9')
        self.assertNotContains(response, 'MacBook Pro')

    def test_mobile_products_show_cash_price_and_lipa_pole_pole_plan(self):
        category = ProductCategory.objects.create(name='Smartphones', slug='smartphones')
        laptop_category = ProductCategory.objects.create(name='Laptops', slug='laptops')

        mobile_product = Product.objects.create(
            name='Pixel 9',
            brand='Google',
            category=category,
            price=Decimal('12000.00'),
            stock_quantity=3,
            description='Flagship smartphone',
            device_type='mobile',
            condition='new',
        )
        laptop_product = Product.objects.create(
            name='MacBook Air',
            brand='Apple',
            category=laptop_category,
            price=Decimal('150000.00'),
            stock_quantity=2,
            description='Laptop computer',
            device_type='laptop',
            condition='new',
        )

        self.assertTrue(mobile_product.supports_lipa_pole_pole)
        self.assertFalse(laptop_product.supports_lipa_pole_pole)
        self.assertEqual(mobile_product.lipa_pole_pole_deposit, Decimal('3600.00'))
        self.assertEqual(mobile_product.lipa_pole_pole_daily_payment, Decimal('23.33'))

        response = self.client.get('/products/')

        self.assertContains(response, 'Cash price')
        self.assertContains(response, 'Lipa Pole Pole')
        self.assertContains(response, 'Deposit')
        self.assertContains(response, 'Daily payment')

    def test_product_image_is_rendered_on_catalog_and_detail_pages(self):
        category = ProductCategory.objects.create(name='Audio', slug='audio')
        image = SimpleUploadedFile('speaker.png', b'fake-image-content', content_type='image/png')
        product = Product.objects.create(
            name='Speaker Mini',
            brand='JBL',
            category=category,
            price=Decimal('129.00'),
            stock_quantity=4,
            description='Compact speaker',
            device_type='mobile',
            condition='new',
            image=image,
        )

        product_list_response = self.client.get('/products/')
        product_detail_response = self.client.get(f'/products/{product.pk}/')

        self.assertEqual(product_list_response.status_code, 200)
        self.assertEqual(product_detail_response.status_code, 200)
        self.assertContains(product_list_response, 'speaker')
        self.assertContains(product_detail_response, 'speaker')
