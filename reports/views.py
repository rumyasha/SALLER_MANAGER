# reports/views.py
from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import Http404
from orders.models import Order, OrderItem
from utils.pdf_utils import generate_sales_report
from datetime import datetime

def sales_report_pdf(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return HttpResponse('Не переданы параметры start или end', status=400)
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse('Неверный формат даты, используйте YYYY-MM-DD', status=400)

    # Выбираем заказы по дате
    orders_qs = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

    # Общая выручка и кол-во
    total_revenue = orders_qs.aggregate(sum=Sum('total_amount'))['sum'] or 0
    order_count = orders_qs.count()

    # Топ-5 клиентов
    top_customers = (
        orders_qs
        .values('customer__full_name')
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:5]
    )

    # Самый популярный товар
    popular = (
        OrderItem.objects
        .filter(order__in=orders_qs)
        .values('product__name')
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')
        .first()
    )
    popular_product = popular['product__name'] if popular else '—'

    # Таблица заказов
    orders = [
        {
            'date': o.created_at.date(),
            'customer': o.customer.full_name,
            'sum': o.total_amount,
            'status': o.status,
        }
        for o in orders_qs.select_related('customer')
    ]

    context = {
        'total_revenue': total_revenue,
        'order_count': order_count,
        'top_customers': top_customers,
        'popular_product': popular_product,
        'orders': orders,
    }

    pdf = generate_sales_report(context, start_date, end_date)
    response = HttpResponse(pdf, content_type='application/pdf')
    fname = f"sales_report_{start}_{end}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response
