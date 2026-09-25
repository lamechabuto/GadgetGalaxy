from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Choose a username',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Enter your email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Confirm your password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email', max_length=254)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Username or email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'auth-input',
            'placeholder': 'Password',
        })

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(email__iexact=username)
                username = user.username
            except User.DoesNotExist:
                pass

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )

        return self.cleaned_data
