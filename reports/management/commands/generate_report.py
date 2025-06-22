from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.views import sales_report_pdf
from django.test import RequestFactory


class Command(BaseCommand):
    help = 'Генерирует PDF отчет о продажах за последний месяц'

    def handle(self, *args, **options):
        factory = RequestFactory()
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)

        request = factory.get(f'/api/reports/sales/?start={start_date}&end={end_date}')
        response = sales_report_pdf(request)

        with open(f'sales_report_{start_date}_to_{end_date}.pdf', 'wb') as f:
            f.write(response.content)

        self.stdout.write(self.style.SUCCESS(f'Отчет создан: sales_report_{start_date}_to_{end_date}.pdf'))