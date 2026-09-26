from django.urls import path

from .views import contact_page, privacy_policy, terms_and_conditions

urlpatterns = [
    path('', contact_page, name='contact_page'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-conditions/', terms_and_conditions, name='terms_and_conditions'),
]
