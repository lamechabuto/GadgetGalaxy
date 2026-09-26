from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from sales.models import SaleOrder


class SaleOrderPendingExpiryTests(TestCase):
    def test_expired_pending_orders_are_cancelled_after_12_hours(self):
        expired_order = SaleOrder.objects.create(customer_name='Expired Buyer')
        fresh_order = SaleOrder.objects.create(customer_name='Fresh Buyer')

        SaleOrder.objects.filter(pk=expired_order.pk).update(
            created_at=timezone.now() - timedelta(hours=13)
        )
        SaleOrder.objects.filter(pk=fresh_order.pk).update(
            created_at=timezone.now() - timedelta(hours=11)
        )

        SaleOrder.cancel_expired_pending_orders()

        expired_order.refresh_from_db()
        fresh_order.refresh_from_db()

        self.assertEqual(expired_order.status, 'cancelled')
        self.assertEqual(fresh_order.status, 'pending')
