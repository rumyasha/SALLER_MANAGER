from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company_name', 'phone', 'created_at')
    search_fields = ('full_name', 'email', 'company_name', 'phone')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'