from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',
            'patient',
            'date',
            'time',
            'reason',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
