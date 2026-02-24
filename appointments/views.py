from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Appointment.objects.select_related('doctor__user', 'patient__user').all()
        user = self.request.user

        if user.role == 'ADMIN':
            return queryset
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            return queryset.filter(doctor=user.doctor_profile)
        if user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            return queryset.filter(patient=user.patient_profile)
        return queryset.none()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            if self.request.user.role not in ['ADMIN', 'DOCTOR']:
                return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            serializer.save(patient=user.patient_profile)
            return
        serializer.save()
