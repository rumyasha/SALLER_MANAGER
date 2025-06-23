import os
from django.conf import settings
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_sales_report(context, start_date, end_date):
    """
    context: dict с ключами total_revenue, order_count, top_customers,
             popular_product, orders (список dict)
    start_date, end_date: date
    """
    templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('reports/report.html')

    html_out = tmpl.render(
        start_date=start_date,
        end_date=end_date,
        total_revenue=context['total_revenue'],
        order_count=context['order_count'],
        top_customers=context['top_customers'],
        popular_product=context['popular_product'],
        orders=context['orders'],
    )
    # Генерация PDF
    pdf = HTML(string=html_out, base_url=settings.BASE_DIR).write_pdf()
    return pdf
