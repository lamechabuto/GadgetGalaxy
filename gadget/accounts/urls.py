from django.urls import path

from .views import login_view, logout_view, profile_home, signup_view

urlpatterns = [
    path('', profile_home, name='profile_home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
]
