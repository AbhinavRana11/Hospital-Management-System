from django.contrib import admin

from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'created_at')
    search_fields = ('appointment__doctor__user__username', 'appointment__patient__user__username')
