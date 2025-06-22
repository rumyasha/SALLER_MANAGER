import django_filters
from .models import Order
from django.db.models import Q

class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    total_amount = django_filters.RangeFilter()
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Order
        fields = ['status', 'customer']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(customer__full_name__icontains=value) |
            Q(customer__email__icontains=value) |
            Q(customer__company_name__icontains=value) |
            Q(items__product__name__icontains=value)
        ).distinct()