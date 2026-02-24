from rest_framework import serializers

from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'appointment', 'amount', 'paid', 'issued_at']
        read_only_fields = ['id', 'issued_at']
