from django.contrib import admin

from .models import SalesReport


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'total_orders', 'total_revenue', 'total_units_sold')
    search_fields = ('report_date',)
