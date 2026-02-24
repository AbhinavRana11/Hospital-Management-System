from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return Invoice.objects.select_related('appointment__doctor__user', 'appointment__patient__user').all()

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        paid_invoices = self.get_queryset().filter(paid=True)
        unpaid_invoices = self.get_queryset().filter(paid=False)
        return Response(
            {
                'total_revenue': paid_invoices.aggregate(total=Sum('amount'))['total'] or 0,
                'paid_count': paid_invoices.count(),
                'unpaid_count': unpaid_invoices.count(),
                'pending_amount': unpaid_invoices.aggregate(total=Sum('amount'))['total'] or 0,
            }
        )
