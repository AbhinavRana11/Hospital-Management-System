from django.db import models
from appointments.models import Appointment


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    diagnosis = models.TextField()
    medicines = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for Appointment #{self.appointment_id}"
