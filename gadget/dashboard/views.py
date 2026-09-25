from django.db.models import Sum
from django.shortcuts import render

from inventory.models import InventoryItem
from products.models import Product
from sales.models import SaleOrder


def dashboard_home(request):
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(total_stock=Sum('stock_quantity'))['total_stock'] or 0
    total_orders = SaleOrder.objects.count()
    revenue = SaleOrder.objects.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
    low_stock_items = Product.objects.filter(stock_quantity__lte=5).count()
    recent_inventory = InventoryItem.objects.select_related('product')[:5]
    recent_orders = SaleOrder.objects.order_by('-created_at')[:5]
    top_products = Product.objects.order_by('-stock_quantity')[:5]
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]

    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        'total_orders': total_orders,
        'revenue': revenue,
        'low_stock_items': low_stock_items,
        'recent_inventory': recent_inventory,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'featured_products': featured_products,
    }
    return render(request, 'dashboard/home.html', context)
