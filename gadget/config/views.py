from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import ContactMessage


def contact_page(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        message = (request.POST.get('message') or '').strip()

        if not name or not email or not message:
            return render(request, 'config/contact.html', {
                'error': 'Please provide your name, email, and message.',
                'form_data': {'name': name, 'email': email, 'phone': phone, 'message': message},
            })

        contact = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message,
        )

        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@gadgetgalaxy.com')
        send_mail(
            subject=f'New contact message from {name}',
            message=(
                f'Name: {name}\n'
                f'Email: {email}\n'
                f'Phone: {phone or "Not provided"}\n\n'
                f'Message:\n{message}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )

        request.session['contact_message_success'] = (
            'Thanks for contacting us. Our admin team has received your message.'
        )
        return redirect(reverse('contact_page'))

    success_message = request.session.pop('contact_message_success', '')
    return render(request, 'config/contact.html', {
        'success_message': success_message,
        'form_data': {'name': '', 'email': '', 'phone': '', 'message': ''},
    })
