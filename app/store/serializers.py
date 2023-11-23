from rest_framework import serializers
from .models import Product, Category, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    merchant = serializers.ReadOnlyField(source='merchant.id')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'thumbnail', 'merchant']


class OrderItemSerializer(serializers.ModelSerializer):
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'product_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['delivery_address', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        customer = self.context['request'].user
        order = Order.objects.create(customer=customer, **validated_data)
        total_price = 0
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total_price += item.product.price * item.quantity
        order.total_price = total_price
        order.save()
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_price'] = instance.total_price
        representation['customer'] = instance.customer.id
        return representation