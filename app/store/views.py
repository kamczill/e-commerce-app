from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core.mail import send_mail
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .models import Product, Category, Order
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OrderItem
from django.db.models import Count, Q
from datetime import datetime

# custom permission class
class IsMerchantUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_merchant

class IsMerchantOrSuperuser(permissions.BasePermission):
    """
    Allows access only to merchant or superuser users for write operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_merchant or request.user.is_superuser)

class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request):
        return request.user.is_authenticated and request.user.is_superuser

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsMerchantOrSuperuser]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperuser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'category', 'description', 'price']
    ordering_fields = ['name', 'category', 'price']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsMerchantUser]

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user)

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsMerchantUser]

    def get_queryset(self):
        """Ensure a merchant can only update their own products."""
        user = self.request.user
        return user.products.all()

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsMerchantUser]

    def get_queryset(self):
        """Ensure a merchant can only update their own products."""
        user = self.request.user
        return user.products.all()

class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save()
        # Send confirmation email
        send_mail(
            'Order Confirmation',
            f'Your order with ID {order.id} has been placed successfully.',
            'from@example.com',
            [order.customer.email],
            fail_silently=False,
        )

class ProductStatisticsView(APIView):
    permission_classes = [IsMerchantUser]  # Custom permission class for merchant status

    def get(self, request, date_from, date_to, num_products):
        # Convert date strings to datetime objects
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            num_products = int(num_products)
        except ValueError:
            return Response({"error": "Invalid date format or number. Use YYYY-MM-DD for dates and an integer for number of products."}, status=400)

        # Query the OrderItem model
        product_stats = OrderItem.objects.filter(
            order__order_date__range=(date_from, date_to)
        ).values(
            'product__name'
        ).annotate(
            total_ordered=Count('id')
        ).order_by('-total_ordered')[:num_products]

        return Response(product_stats)