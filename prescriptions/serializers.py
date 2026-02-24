from rest_framework import serializers

from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'diagnosis', 'medicines', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
