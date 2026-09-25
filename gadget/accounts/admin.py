from django.contrib import admin

from .models import CustomerProfile, StaffProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country')
    search_fields = ('user__username', 'phone', 'city')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'department')
