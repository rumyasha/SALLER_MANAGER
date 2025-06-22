from django.db import models

class Product(models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True, null=True)
    price = models.DecimalField('Цена (KZT)', max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField('Количество на складе', default=0)
    is_active = models.BooleanField('Доступен для заказа', default=True)
    discount_percent = models.DecimalField(
        'Скидка на товар (%)',
        max_digits=5,
        decimal_places=2,
        default=0.0
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.price} KZT"