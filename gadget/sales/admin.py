from django.contrib import admin

from .models import SaleOrder, SaleOrderItem


class SaleOrderItemInline(admin.TabularInline):
    model = SaleOrderItem
    extra = 0


@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_email')
    inlines = [SaleOrderItemInline]


@admin.register(SaleOrderItem)
class SaleOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    search_fields = ('product__name', 'order__customer_name')
