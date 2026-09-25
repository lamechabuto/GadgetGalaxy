from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm, SignupForm
from .models import CustomerProfile, StaffProfile


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile_home')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.get_or_create(user=user)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_home(request):
    customer_profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    staff_profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    context = {
        'customer_profile': customer_profile,
        'staff_profile': staff_profile,
    }
    return render(request, 'accounts/profile_home.html', context)
