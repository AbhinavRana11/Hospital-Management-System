from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'paid', 'issued_at')
    list_filter = ('paid',)
    search_fields = ('appointment__doctor__user__username', 'appointment__patient__user__username')
