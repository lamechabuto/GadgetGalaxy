from django.shortcuts import render

from sales.models import SaleOrder


def sales_home(request):
    orders = SaleOrder.objects.prefetch_related('items__product').order_by('-created_at')
    context = {
        'orders': orders,
        'total_revenue': sum((order.total_amount for order in orders), 0),
    }
    return render(request, 'sales/sales_home.html', context)
