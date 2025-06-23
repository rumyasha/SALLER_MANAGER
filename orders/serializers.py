from django.core.exceptions import ValidationError
from requests import Response
from rest_framework import serializers, viewsets
from customers.models import Customer
from customers.serializers import CustomerSerializer
from products.models import Product
from products.serializers import ProductSerializer
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'discount_percent']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_id',
            'created_at', 'updated_at', 'status',
            'total_amount', 'tax_amount', 'shipping_cost', 'discount_amount',
            'items'
        ]
        read_only_fields = ['total_amount', 'tax_amount', 'shipping_cost', 'discount_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        order.calculate_totals()
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                OrderItem.objects.create(order=instance, **item)
            instance.calculate_totals()
            instance.save()
        return instance


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        prev_status = instance.status
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Автоматически подтверждаем и списываем товары
        if serializer.validated_data.get('status') == 'confirmed' and prev_status != 'confirmed':
            try:
                instance.confirm()
            except ValidationError as e:
                return Response({'detail': str(e)}, status=400)

        return Response(self.get_serializer(instance).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
