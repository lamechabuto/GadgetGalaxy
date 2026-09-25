from django.contrib import admin

from .models import MpesaTransaction


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'phone_number', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__customer_name', 'merchant_request_id', 'checkout_request_id')
