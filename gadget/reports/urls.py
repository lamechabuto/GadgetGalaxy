from django.urls import path

from .views import reports_home

urlpatterns = [
    path('', reports_home, name='reports_home'),
]
