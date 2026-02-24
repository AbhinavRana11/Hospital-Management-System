from django.db import models
from appointments.models import Appointment


class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - Appointment #{self.appointment_id}"
