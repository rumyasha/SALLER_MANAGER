from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'total_amount', 'status')
    list_filter = ('status', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('customer__full_name', 'customer__email')
    inlines = (OrderItemInline,)
    actions = ['confirm_orders', 'cancel_orders']

    def confirm_orders(self, request, queryset):
        for order in queryset:
            try:
                order.confirm_order()
            except ValueError as e:
                self.message_user(request, str(e), level='ERROR')
        self.message_user(request, f"{queryset.count()} заказов подтверждено")
    confirm_orders.short_description = "Подтвердить выбранные заказы"

    def cancel_orders(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} заказов отменено")
    cancel_orders.short_description = "Отменить выбранные заказы"