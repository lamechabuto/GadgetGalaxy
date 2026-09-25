from cart.models import Cart


def cart_count(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return {'cart_count': cart.total_quantity}
