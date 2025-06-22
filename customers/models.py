from django.db import models

class Customer(models.Model):
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField('Email', unique=True)
    company_name = models.CharField('Компания', max_length=255, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    discount_percent = models.DecimalField(
        'Персональная скидка (%)',
        max_digits=5,
        decimal_places=2,
        default=0.0
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.email})"