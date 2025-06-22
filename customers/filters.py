import django_filters
from .models import Customer

class CustomerFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Customer
        fields = {
            'full_name': ['icontains'],
            'email': ['icontains'],
            'company_name': ['icontains'],
            'phone': ['icontains'],
        }