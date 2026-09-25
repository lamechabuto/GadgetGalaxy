from decimal import Decimal

from django.db import models


class SalesReport(models.Model):
    report_date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_units_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('report_date',)

    def __str__(self):
        return f'{self.report_date} sales report'
