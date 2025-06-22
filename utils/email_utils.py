from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.pdf_utils import generate_pdf


def send_order_confirmation(order):
    subject = f'Подтверждение заказа №{order.id}'
    from_email = 'noreply@yourdomain.com'
    to = [order.customer.email]

    # Текстовая версия
    text_content = f'Ваш заказ №{order.id} подтвержден. Сумма: {order.total_amount} KZT'

    # HTML версия
    html_content = render_to_string('emails/order_confirmation.html', {'order': order})

    # PDF версия
    pdf_file = generate_pdf('reports/order_details.html', {'order': order})

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.attach(f'order_{order.id}.pdf', pdf_file.getvalue(), 'application/pdf')
    email.send()