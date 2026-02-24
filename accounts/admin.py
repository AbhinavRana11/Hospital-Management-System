from django.contrib import admin
from django.utils import timezone

from .models import ContactQuery, Doctor, Patient, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialization', 'license_number')
    search_fields = ('user__username', 'specialization', 'license_number')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'age', 'gender', 'contact_number')
    search_fields = ('user__username', 'contact_number')


@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'dob', 'created_at', 'replied_at')
    search_fields = ('name', 'address', 'problem', 'admin_reply')
    list_filter = ('created_at', 'replied_at')
    fields = ('name', 'age', 'dob', 'address', 'problem', 'admin_reply', 'created_at', 'replied_at')
    readonly_fields = ('created_at', 'replied_at')

    def save_model(self, request, obj, form, change):
        previous_reply = ''
        if change:
            old_obj = ContactQuery.objects.filter(pk=obj.pk).first()
            if old_obj:
                previous_reply = old_obj.admin_reply or ''

        current_reply = (obj.admin_reply or '').strip()
        if current_reply and current_reply != previous_reply and obj.replied_at is None:
            obj.replied_at = timezone.now()

        super().save_model(request, obj, form, change)
