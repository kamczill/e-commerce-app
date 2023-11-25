from rest_framework import generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core.mail import send_mail
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer, ProductStatisticSerializer
from .models import Product, Category, Order
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OrderItem
from django.db.models import Count
from datetime import datetime

# custom permission classes
class IsMerchantUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_merchant

class IsMerchantOrSuperuser(permissions.BasePermission):
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
        user = self.request.user
        return user.products.all()

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsMerchantUser]

    def get_queryset(self):
        user = self.request.user
        return user.products.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        object_id = self.kwargs['pk']
        return Response({'status': 'success', 'message': f'Product with ID {object_id} has been successfully deleted.'}, status=status.HTTP_200_OK)


class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save()
        send_mail(
            'Order Confirmation',
            f'Your order with ID {order.id} has been placed successfully.',
            'from@example.com',
            [order.customer.email],
            fail_silently=False,
        )

class ProductStatisticsView(APIView):
    permission_classes = [IsMerchantUser]
    serializer_class = ProductStatisticSerializer

    def get(self, request, date_from, date_to, num_products):
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            num_products = int(num_products)
        except ValueError:
            return Response({"error": "Invalid date format or number. Use YYYY-MM-DD for dates and an integer for number of products."}, status=400)

        product_stats = OrderItem.objects.filter(
            order__order_date__range=(date_from, date_to)
        ).values(
            'product__name'
        ).annotate(
            total_ordered=Count('id')
        ).order_by('-total_ordered')[:num_products]

        return Response(product_stats)