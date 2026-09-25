from django.core import mail
from django.test import TestCase
from django.urls import reverse

from config.models import ContactMessage


class ContactMessageTests(TestCase):
    def test_contact_form_saves_and_sends_message_to_admin(self):
        response = self.client.post(
            reverse('contact_page'),
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'phone': '+254712345678',
                'message': 'I want to know the available phone deals.',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('I want to know the available phone deals.', mail.outbox[0].body)
        self.assertContains(response, 'Thanks for contacting us')

    def test_contact_page_renders_form_and_whatsapp_link(self):
        response = self.client.get(reverse('contact_page'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact GadgetGalaxy')
        self.assertContains(response, 'Send us a message')
        self.assertContains(response, 'Chat on WhatsApp')
