from django.contrib import admin

from .models import InventoryItem, InventoryMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'reorder_level', 'last_counted_at')
    search_fields = ('product__name', 'warehouse')


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('item', 'movement_type', 'quantity', 'created_at')
    list_filter = ('movement_type',)
    search_fields = ('item__product__name', 'notes')
