from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=120)
    license_number = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ContactQuery(models.Model):
    name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(null=True, blank=True)
    dob = models.DateField()
    address = models.TextField()
    problem = models.TextField()
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Query'
        verbose_name_plural = 'Contact Queries'

    def __str__(self):
        return f"{self.name} - Query #{self.id}"
