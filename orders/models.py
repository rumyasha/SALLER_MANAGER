from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, getcontext
from django.core.exceptions import ValidationError
from customers.models import Customer

getcontext().prec = 10


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('confirmed', 'Подтвержден'),
        ('shipped', 'Отправлен'),
        ('cancelled', 'Отменен'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Клиент'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    total_amount = models.DecimalField(
        'Итоговая сумма',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        'Сумма налогов',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    shipping_cost = models.DecimalField(
        'Стоимость доставки',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        'Сумма скидок',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y')}"

    def clean(self):
        if self.status == 'confirmed' and not self.items.exists():
            raise ValidationError("Нельзя подтвердить пустой заказ")

    def calculate_totals(self):
        items = self.items.select_related('product')
        subtotal = sum(
            Decimal(item.price) * item.quantity * (Decimal('1') - item.discount_percent / Decimal('100'))
            for item in items
        )

        customer_discount = subtotal * (Decimal(self.customer.discount_percent) / Decimal('100'))
        global_discount = subtotal * Decimal('0.1') if subtotal > Decimal('150000') else Decimal('0')
        total_discount = customer_discount + global_discount

        tax = (subtotal - total_discount) * Decimal('0.12')
        shipping = Decimal('500') if subtotal < Decimal('2000') else Decimal('0')

        self.total_amount = subtotal - total_discount + tax + shipping
        self.tax_amount = tax
        self.shipping_cost = shipping
        self.discount_amount = total_discount
        return self.total_amount

    def confirm(self):
        if self.status == 'confirmed':
            return
        with transaction.atomic():
            for item in self.items.select_related('product').select_for_update():
                if item.product.stock_quantity < item.quantity:
                    raise ValidationError(
                        f"Недостаточно товара {item.product.name} на складе. "
                        f"Доступно: {item.product.stock_quantity}, требуется: {item.quantity}"
                    )
            for item in self.items.select_related('product').select_for_update():
                item.product.stock_quantity -= item.quantity
                item.product.save()
            self.status = 'confirmed'
            self.save()

    def cancel(self, restock=True):
        if self.status == 'cancelled':
            return
        with transaction.atomic():
            if restock and self.status == 'confirmed':
                for item in self.items.select_related('product').select_for_update():
                    item.product.stock_quantity += item.quantity
                    item.product.save()
            self.status = 'cancelled'
            self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Процент скидки'
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        ordering = ['id']
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=1), name='quantity_gte_1'),
            models.CheckConstraint(check=models.Q(discount_percent__gte=0) & models.Q(discount_percent__lte=100), name='discount_percent_range'),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Заказ #{self.order_id})"

    def clean(self):
        if not self.price:
            self.price = self.product.price
        if self.product.stock_quantity < self.quantity:
            raise ValidationError(
                f"Недостаточно товара {self.product.name} на складе. "
                f"Доступно: {self.product.stock_quantity}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.calculate_totals()
        self.order.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            previous_status = Order.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Если статус стал confirmed — вызываем confirm()
        if self.status == 'confirmed' and previous_status != 'confirmed':
            self.confirm()
    @property
    def total_price(self):
        return self.price * self.quantity * (Decimal('1') - self.discount_percent / Decimal('100'))
