from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import Product, Order, Category
from user.models import User

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'merchant')
    search_fields = ('name', 'description')
    list_filter = ('category', 'merchant')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order_date', 'total_price')
    search_fields = ('customer__name', 'customer__email')
    list_filter = ('order_date',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'is_active', 'is_staff', 'is_merchant')
    search_fields = ('email', 'name', 'surname')
    list_filter = ('is_active', 'is_staff', 'is_merchant')
