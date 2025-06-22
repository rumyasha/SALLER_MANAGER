import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    price = django_filters.RangeFilter()
    stock_quantity = django_filters.RangeFilter()

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'description': ['icontains'],
            'is_active': ['exact'],
        }