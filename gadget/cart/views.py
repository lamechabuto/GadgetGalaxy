from decimal import Decimal

from django.shortcuts import redirect, render

from cart.models import Cart
from products.models import Product


def _payment_plan_for(total_amount):
    total = Decimal(str(total_amount or '0'))
    deposit = (total * Decimal('0.30')).quantize(Decimal('0.01'))
    remaining_after_deposit = total - deposit
    daily_payment = (remaining_after_deposit / Decimal('360')).quantize(Decimal('0.01'))
    return {
        'deposit': deposit,
        'daily_payment': daily_payment,
    }


def cart_home(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.get('cart_session') or request.session.session_key
    request.session['cart_session'] = session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return render(request, 'cart/cart_home.html', {'cart': cart})


def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.get('cart_session') or request.session.session_key
    request.session['cart_session'] = session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    cart.add_item(product, quantity=1)
    return redirect('product_list')


from payments.services import MpesaSTKService


def checkout_view(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.get('cart_session') or request.session.session_key
    request.session['cart_session'] = session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    payment_plan = _payment_plan_for(cart.total_amount)
    has_mobile_items = cart.items.filter(product__device_type='mobile').exists()

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        payment_method = request.POST.get('payment_method', 'cash').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        if not customer_name:
            return render(request, 'cart/checkout.html', {
                'cart': cart,
                'payment_plan': payment_plan,
                'has_mobile_items': has_mobile_items,
                'error': 'Customer name is required.',
            })
        if not has_mobile_items and payment_method == 'lipa_pole_pole':
            payment_method = 'cash'
        if payment_method not in {'lipa_pole_pole', 'cash', 'mpesa'}:
            payment_method = 'cash'
        order = cart.checkout(customer_name, customer_email, payment_method)
        if payment_method == 'mpesa':
            if not phone_number:
                return render(request, 'cart/checkout.html', {
                    'cart': cart,
                    'payment_plan': payment_plan,
                    'has_mobile_items': has_mobile_items,
                    'error': 'A valid phone number is required for M-Pesa STK Push.',
                })
            try:
                MpesaSTKService().initiate_stk_push(order, phone_number)
            except ValueError:
                return render(request, 'cart/checkout.html', {
                    'cart': cart,
                    'payment_plan': payment_plan,
                    'has_mobile_items': has_mobile_items,
                    'error': 'M-Pesa is not configured yet. Please contact the admin.',
                })
            return render(request, 'cart/checkout_success.html', {'order': order})
        return render(request, 'cart/checkout_success.html', {'order': order})

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'payment_plan': payment_plan,
        'has_mobile_items': has_mobile_items,
    })
