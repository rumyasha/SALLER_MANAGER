from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_customer_discount(sender, instance, **kwargs):
    if instance.status == 'confirmed':
        total_orders = Order.objects.filter(
            customer=instance.customer,
            status='confirmed'
        ).count()

        if total_orders > 5:
            instance.customer.discount_percent = 15
            instance.customer.save()