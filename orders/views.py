import json

from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .forms import OrderItemFormSet
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .filters import OrderFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from products.models import Product



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_at', 'total_amount']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            order.confirm_order()
            return Response({'status': 'order confirmed'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'confirmed':
            for item in order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save()

        order.status = 'cancelled'
        order.save()
        return Response({'status': 'order cancelled'})


class OrderCreateView(CreateView):
    model = Order
    fields = ['customer']
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('order-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        try:
            order = form.save()

            # Обрабатываем товары вручную
            i = 0
            while f'items-{i}-product' in self.request.POST:
                OrderItem.objects.create(
                    order=order,
                    product_id=self.request.POST[f'items-{i}-product'],
                    quantity=self.request.POST[f'items-{i}-quantity'],
                    discount_percent=self.request.POST.get(f'items-{i}-discount_percent', 0)
                )
                i += 1

            order.calculate_totals()
            return super().form_valid(form)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)