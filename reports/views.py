from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
from orders.models import Order, OrderItem
from customers.models import Customer


def sales_report_pdf(request):
    # Получаем параметры дат из запроса
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    # Проверяем наличие обязательных параметров
    if not start_date or not end_date:
        return HttpResponse("Необходимо указать start и end даты", status=400)

    try:
        # Парсим даты
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Неверный формат даты. Используйте YYYY-MM-DD", status=400)

    # Получаем заказы за период
    orders = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).select_related('customer').prefetch_related('items')

    # Рассчитываем общую статистику
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders.count()

    # Топ-5 клиентов по выручке
    top_customers = Customer.objects.filter(
        orders__in=orders
    ).annotate(
        total_spent=Sum('orders__total_amount')
    ).order_by('-total_spent')[:5]

    # Самые популярные товары
    popular_products = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    # Подготавливаем контекст для шаблона
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'order_count': order_count,
        'top_customers': top_customers,
        'popular_products': popular_products,
        'orders': orders,
    }

    # Рендерим HTML из шаблона
    html_string = render_to_string('reports/sales_report.html', context)

    # Создаем HTTP-ответ с PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.pdf"'

    # Генерируем PDF
    pisa_status = pisa.CreatePDF(
        html_string,
        dest=response,
        encoding='UTF-8'
    )

    # Если возникла ошибка при генерации PDF
    if pisa_status.err:
        return HttpResponse('Ошибка при генерации PDF', status=500)

    return response