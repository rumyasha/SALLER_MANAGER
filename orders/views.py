from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .forms import OrderForm, OrderItemFormSet
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            order.confirm()
            return Response({'status': 'order confirmed'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.cancel()
        return Response({'status': 'order cancelled'})

def order_create_view(request):
    # POST: bind OrderForm first
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # create but don't save to DB yet
            order = form.save(commit=False)
            # bind formset to this new order instance
            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                # save order to get a primary key
                order.save()
                # save all items with order FK
                formset.save()
                # recalculate totals and save
                order.calculate_totals()
                order.save()
                return redirect('order-list')
        else:
            formset = OrderItemFormSet(request.POST)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    return render(request, 'orders/order_form.html', {'form': form, 'formset': formset})