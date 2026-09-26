from django.test import TestCase

from accounts.forms import SignupForm


class SignupFormUsernameTests(TestCase):
    def test_username_allows_spaces_for_real_name_style_usernames(self):
        form = SignupForm(data={
            'username': 'Jane Doe',
            'email': 'jane@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertTrue(form.is_valid(), form.errors)
