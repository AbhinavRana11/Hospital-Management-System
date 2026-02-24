from django.db import models
from accounts.models import Doctor, Patient


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} {self.time}"
