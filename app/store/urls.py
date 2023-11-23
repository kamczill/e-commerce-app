from django.urls import path
from .views import ProductListView

urlpatterns = [
    # ... other url patterns ...
    path('products/', ProductListView.as_view(), name='product-list'),
]