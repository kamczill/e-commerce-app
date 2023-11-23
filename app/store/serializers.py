from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    merchant = serializers.ReadOnlyField(source='merchant.id')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'thumbnail', 'merchant']
