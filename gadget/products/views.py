from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from products.models import Product


def product_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    products = Product.objects.select_related('category').all().order_by('brand', 'name')

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    categories = products.model.category.field.related_model.objects.all().order_by('name')

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query,
        'category_slug': category_slug,
        'categories': categories,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'products/product_detail.html', {'product': product})
