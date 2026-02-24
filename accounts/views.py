from datetime import date

from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import redirect, render
from django.db.models import Count, Sum
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment
from billing.models import Invoice
from prescriptions.models import Prescription

from .forms import AppointmentBookForm, ContactQueryForm, DoctorRegisterForm, LoginForm, PatientRegisterForm
from .models import ContactQuery, Doctor, Patient, User
from .permissions import IsAdminRole
from .serializers import DoctorSerializer, PatientSerializer, RegisterSerializer, UserSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return Doctor.objects.select_related('user').all()


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return Patient.objects.select_related('user').all()


class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        cache_key = 'dashboard_stats'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        appointment_counts = Appointment.objects.values('status').annotate(total=Count('id'))
        revenue = Invoice.objects.filter(paid=True).aggregate(total_revenue=Sum('amount'))

        data = {
            'users': {
                'doctors': Doctor.objects.count(),
                'patients': Patient.objects.count(),
            },
            'appointments_by_status': list(appointment_counts),
            'revenue': revenue['total_revenue'] or 0,
            'paid_invoices': Invoice.objects.filter(paid=True).count(),
            'unpaid_invoices': Invoice.objects.filter(paid=False).count(),
        }
        cache.set(cache_key, data, timeout=300)
        return Response(data)


def register_options_view(request):
    return render(request, 'register.html')


def login_options_view(request):
    return render(request, 'login.html')


def guest_user_view(request):
    return render(request, 'guest_user.html')


def register_patient_view(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save_user(role='PATIENT')
            dob = form.cleaned_data.get('dob')
            age = None
            if dob:
                age = max(0, date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day)))
            Patient.objects.create(user=user, dob=dob, age=age)
            messages.success(request, 'Patient account created successfully. You can now log in.')
            return redirect('/')
    else:
        form = PatientRegisterForm()
    return render(request, 'register_patient.html', {'form': form})


def register_doctor_view(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save_user(role='DOCTOR')
            user.is_active = False
            user.save(update_fields=['is_active'])
            Doctor.objects.create(
                user=user,
                specialization=form.cleaned_data['specialization'],
                license_number=form.cleaned_data['license_number'],
            )
            messages.success(request, 'Doctor account created. Approval from admin is pending.')
            return redirect('/')
    else:
        form = DoctorRegisterForm()
    return render(request, 'register_doctor.html', {'form': form})


def login_patient_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is None:
                messages.error(request, 'Invalid credentials. Please try again.')
            elif user.role != 'PATIENT':
                messages.error(request, 'This is patient login. Please use the correct portal.')
            elif not user.is_active:
                messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                login(request, user)
                messages.success(request, 'Logged in successfully as patient.')
                return redirect('/patient/')
    else:
        form = LoginForm()
    return render(request, 'login_patient.html', {'form': form})


def login_doctor_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is None:
                messages.error(request, 'Invalid credentials. Please try again.')
            elif user.role != 'DOCTOR':
                messages.error(request, 'This is doctor login. Please use the correct portal.')
            elif not user.is_active:
                messages.error(request, 'Doctor account approval from admin is pending.')
            else:
                login(request, user)
                messages.success(request, 'Logged in successfully as doctor.')
                return redirect('/doctor/')
    else:
        form = LoginForm()
    return render(request, 'login_doctor.html', {'form': form})


def login_admin_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            matched_user = User.objects.filter(email__iexact=email).first()
            login_username = matched_user.username if matched_user else email
            user = authenticate(request, username=login_username, password=password)
            if user is None:
                messages.error(request, 'Invalid credentials. Please try again.')
            elif not user.is_active:
                messages.error(request, 'Your account is inactive.')
            elif not (user.is_staff or user.is_superuser or user.role == 'ADMIN'):
                messages.error(request, 'This is admin login. Use the correct portal.')
            else:
                if user.role == 'ADMIN' and not user.is_staff:
                    user.is_staff = True
                    user.save(update_fields=['is_staff'])
                login(request, user)
                messages.success(request, 'Logged in successfully as admin.')
                return redirect('/admin/')
    else:
        form = LoginForm()
    return render(request, 'login_admin.html', {'form': form})


def admin_page_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as admin first.')
        return redirect('/login/admin/')

    if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'ADMIN'):
        messages.error(request, 'You are not authorized to access admin page.')
        return redirect('/login/')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve_doctor':
            doctor_id = request.POST.get('doctor_id')
            doctor = Doctor.objects.select_related('user').filter(id=doctor_id).first()
            if doctor is not None:
                doctor.user.is_active = True
                doctor.user.save(update_fields=['is_active'])
                messages.success(request, f'Doctor {doctor.user.get_full_name() or doctor.user.username} approved successfully.')
            return redirect('/admin/')

        if action == 'reject_doctor':
            doctor_id = request.POST.get('doctor_id')
            doctor = Doctor.objects.select_related('user').filter(id=doctor_id).first()
            if doctor is not None:
                doctor_name = doctor.user.get_full_name() or doctor.user.username
                doctor.user.delete()
                messages.success(request, f'Doctor {doctor_name} rejected and removed successfully.')
            return redirect('/admin/')

        query_id = request.POST.get('query_id')
        reply_text = (request.POST.get('admin_reply') or '').strip()
        if query_id:
            query = ContactQuery.objects.filter(id=query_id).first()
            if query is not None:
                query.admin_reply = reply_text
                query.replied_at = timezone.now() if reply_text else None
                query.save(update_fields=['admin_reply', 'replied_at'])
                messages.success(request, 'Reply saved successfully.')
        return redirect('/admin/')

    queries = ContactQuery.objects.all()
    doctors = Doctor.objects.select_related('user').all()
    pending_doctors = doctors.filter(user__is_active=False)
    patients = Patient.objects.select_related('user').prefetch_related('appointments__doctor__user').all()
    appointments = Appointment.objects.select_related('doctor__user', 'patient__user').prefetch_related('invoice').all()
    
    context = {
        'doctors': doctors,
        'pending_doctors': pending_doctors,
        'patients': patients,
        'appointments': appointments,
        'queries': queries,
        'doctor_count': doctors.count(),
        'pending_doctor_count': pending_doctors.count(),
        'patient_count': patients.count(),
        'appointment_count': appointments.count(),
        'query_count': queries.count(),
        'replied_count': queries.exclude(admin_reply='').count(),
    }
    return render(request, 'admin.html', context)


def admin_billing_history_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as admin first.')
        return redirect('/login/admin/')

    if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'ADMIN'):
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('/login/')

    # Get all invoices with related data
    invoices = Invoice.objects.select_related('appointment__patient__user', 'appointment__doctor__user').all()
    
    # Calculate totals
    total_paid = invoices.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    total_pending = invoices.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    total_all = total_paid + total_pending
    
    context = {
        'invoices': invoices,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_all': total_all,
        'paid_count': invoices.filter(paid=True).count(),
        'pending_count': invoices.filter(paid=False).count(),
    }
    return render(request, 'admin_billing_history.html', context)


def book_appointment_gate_view(request):
    if not request.user.is_authenticated:
        return render(request, 'book_appointment_gate.html')
    
    if request.user.role != 'PATIENT':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('/')
    
    try:
        patient_profile = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('/login/')
    
    specialization_filter = request.GET.get('specialization', '')
    form = AppointmentBookForm()
    
    # Filter doctors by specialization if provided
    if specialization_filter:
        form.fields['doctor'].queryset = Doctor.objects.select_related('user').filter(
            user__is_active=True,
            specialization__icontains=specialization_filter
        )
    
    if request.method == 'POST':
        form = AppointmentBookForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient_profile
            appointment.status = 'SCHEDULED'
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Awaiting doctor confirmation.')
            return redirect('/patient/')
    
    # Get all unique specializations for the datalist
    specializations = Doctor.objects.filter(user__is_active=True).values_list('specialization', flat=True).distinct()
    
    context = {
        'form': form,
        'specializations': specializations,
        'selected_specialization': specialization_filter,
    }
    return render(request, 'book_appointment.html', context)


def about_us_view(request):
    return render(request, 'about_us.html')


def contact_us_view(request):
    if request.method == 'POST':
        form = ContactQueryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your query has been submitted. Admin will reply soon.')
            return redirect('/contact-us/')
    else:
        form = ContactQueryForm()
    return render(request, 'contact_us.html', {'form': form})


def doctor_page_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as doctor first.')
        return redirect('/login/doctor/')

    if request.user.role != 'DOCTOR':
        messages.error(request, 'You are not authorized to access doctor page.')
        return redirect('/login/')

    try:
        doctor_profile = request.user.doctor_profile
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('/login/')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm_appointment':
            appt_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.filter(id=appt_id, doctor=doctor_profile).first()
            if appointment:
                appointment.status = 'COMPLETED'
                appointment.save(update_fields=['status'])
                messages.success(request, f'Appointment #{appt_id} confirmed successfully.')
            return redirect('/doctor/')

        if action == 'reject_appointment':
            appt_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.filter(id=appt_id, doctor=doctor_profile).first()
            if appointment:
                appointment.status = 'CANCELLED'
                appointment.save(update_fields=['status'])
                messages.success(request, f'Appointment #{appt_id} rejected successfully.')
            return redirect('/doctor/')

        if action == 'create_prescription':
            appt_id = request.POST.get('appointment_id')
            diagnosis = request.POST.get('diagnosis', '').strip()
            medicines = request.POST.get('medicines', '').strip()
            notes = request.POST.get('notes', '').strip()
            appointment = Appointment.objects.filter(id=appt_id, doctor=doctor_profile).first()
            if appointment and diagnosis and medicines:
                Prescription.objects.update_or_create(
                    appointment=appointment,
                    defaults={'diagnosis': diagnosis, 'medicines': medicines, 'notes': notes}
                )
                messages.success(request, f'Prescription saved for Appointment #{appt_id}.')
            return redirect('/doctor/')

        if action == 'create_bill':
            appt_id = request.POST.get('appointment_id')
            amount = request.POST.get('amount', '').strip()
            appointment = Appointment.objects.filter(id=appt_id, doctor=doctor_profile).first()
            if appointment and amount:
                try:
                    amount_decimal = float(amount)
                    Invoice.objects.update_or_create(
                        appointment=appointment,
                        defaults={'amount': amount_decimal, 'paid': False}
                    )
                    messages.success(request, f'Bill created for Appointment #{appt_id}.')
                except ValueError:
                    messages.error(request, 'Invalid amount entered.')
            return redirect('/doctor/')

    appointments = Appointment.objects.filter(doctor=doctor_profile).select_related('patient__user').prefetch_related('prescription', 'invoice')
    scheduled_appointments = appointments.filter(status='SCHEDULED')
    completed_appointments = appointments.filter(status='COMPLETED')
    cancelled_appointments = appointments.filter(status='CANCELLED')

    context = {
        'doctor': doctor_profile,
        'appointments': appointments,
        'scheduled_appointments': scheduled_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_appointments': appointments.count(),
        'scheduled_count': scheduled_appointments.count(),
        'completed_count': completed_appointments.count(),
        'cancelled_count': cancelled_appointments.count(),
    }
    return render(request, 'doctor.html', context)


def patient_page_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as patient first.')
        return redirect('/login/patient/')

    if request.user.role != 'PATIENT':
        messages.error(request, 'You are not authorized to access patient page.')
        return redirect('/login/')

    try:
        patient_profile = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('/login/')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel_appointment':
            appt_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.filter(id=appt_id, patient=patient_profile).first()
            if appointment:
                if appointment.status == 'CANCELLED':
                    messages.error(request, 'Appointment is already cancelled.')
                else:
                    appointment.status = 'CANCELLED'
                    appointment.save(update_fields=['status'])
                    messages.success(request, f'Appointment #{appt_id} cancelled successfully.')
            return redirect('/patient/')

        if action == 'pay_bill':
            appt_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.filter(id=appt_id, patient=patient_profile).first()
            if appointment and hasattr(appointment, 'invoice'):
                invoice = appointment.invoice
                if not invoice.paid:
                    invoice.paid = True
                    invoice.save(update_fields=['paid'])
                    messages.success(request, f'Payment of ${invoice.amount} received successfully for Appointment #{appt_id}.')
                else:
                    messages.error(request, 'This appointment has already been paid.')
            return redirect('/patient/')

    appointments = Appointment.objects.filter(patient=patient_profile).select_related('doctor__user').prefetch_related('prescription', 'invoice')
    scheduled_appointments = appointments.filter(status='SCHEDULED')
    completed_appointments = appointments.filter(status='COMPLETED')
    cancelled_appointments = appointments.filter(status='CANCELLED')

    context = {
        'patient': patient_profile,
        'appointments': appointments,
        'scheduled_appointments': scheduled_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_appointments': appointments.count(),
        'scheduled_count': scheduled_appointments.count(),
        'completed_count': completed_appointments.count(),
        'cancelled_count': cancelled_appointments.count(),
    }
    return render(request, 'patient.html', context)


def doctor_billing_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login as doctor first.')
        return redirect('/login/doctor/')

    if request.user.role != 'DOCTOR':
        messages.error(request, 'You are not authorized to access billing page.')
        return redirect('/login/')

    try:
        doctor_profile = request.user.doctor_profile
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('/login/')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_bill':
            appt_id = request.POST.get('appointment_id')
            amount = request.POST.get('amount', '').strip()
            appointment = Appointment.objects.filter(id=appt_id, doctor=doctor_profile).first()
            if appointment and amount:
                try:
                    amount_decimal = float(amount)
                    if amount_decimal <= 0:
                        messages.error(request, 'Amount must be greater than zero.')
                    else:
                        Invoice.objects.update_or_create(
                            appointment=appointment,
                            defaults={'amount': amount_decimal, 'paid': False}
                        )
                        messages.success(request, f'Bill of ${amount_decimal} created for Appointment #{appt_id}.')
                except ValueError:
                    messages.error(request, 'Invalid amount entered.')
            else:
                messages.error(request, 'Please select an appointment and enter an amount.')
            return redirect('/doctor/billing/')

    # Get all completed appointments for this doctor that may need billing
    completed_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        status='COMPLETED'
    ).select_related('patient__user').prefetch_related('invoice')

    context = {
        'doctor': doctor_profile,
        'completed_appointments': completed_appointments,
        'total_appointments': completed_appointments.count(),
    }
    return render(request, 'doctor_billing.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')
