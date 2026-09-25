from django.shortcuts import render

from inventory.models import InventoryItem, InventoryMovement


def inventory_home(request):
    inventory_items = InventoryItem.objects.select_related('product').all().order_by('product__brand', 'product__name')
    recent_movements = InventoryMovement.objects.select_related('item__product').order_by('-created_at')[:10]
    context = {
        'inventory_items': inventory_items,
        'recent_movements': recent_movements,
    }
    return render(request, 'inventory/inventory_home.html', context)
