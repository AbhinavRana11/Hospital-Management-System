from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Prescription.objects.select_related(
            'appointment__doctor__user',
            'appointment__patient__user',
        ).all()

        user = self.request.user
        if user.role == 'ADMIN':
            return queryset
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            return queryset.filter(appointment__doctor=user.doctor_profile)
        if user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            return queryset.filter(appointment__patient=user.patient_profile)
        return queryset.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if self.request.user.role not in ['ADMIN', 'DOCTOR']:
                return [permissions.IsAdminUser()]
        return super().get_permissions()
