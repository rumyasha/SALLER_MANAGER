from django.urls import path
from .views import sales_report_pdf

urlpatterns = [
    path('sales/', sales_report_pdf, name='sales-report'),
]