from django.contrib import admin

from .models import Product, ProductCategory, ProductInventoryLog


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'category', 'price', 'stock_quantity', 'device_type', 'is_active', 'image')
    list_filter = ('device_type', 'condition', 'is_active', 'category')
    search_fields = ('brand', 'name', 'description')


@admin.register(ProductInventoryLog)
class ProductInventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_quantity', 'reason', 'created_at')
    list_filter = ('reason',)
    search_fields = ('product__name', 'reason')
