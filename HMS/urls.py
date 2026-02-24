from django.shortcuts import render

from accounts.views import (
    admin_billing_history_view,
    admin_page_view,
    about_us_view,
    book_appointment_gate_view,
    contact_us_view,
    doctor_billing_view,
    doctor_page_view,
    guest_user_view,
    login_admin_view,
    login_doctor_view,
    login_options_view,
    login_patient_view,
    logout_view,
    patient_page_view,
    register_doctor_view,
    register_options_view,
    register_patient_view,
)
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def root_view(request):
    return render(request, 'home.html')


urlpatterns = [
    path('', root_view, name='root'),
    path('about-us/', about_us_view, name='about-us'),
    path('contact-us/', contact_us_view, name='contact-us'),
    path('guest/', guest_user_view, name='guest-user'),
    path('book-appointment/', book_appointment_gate_view, name='book-appointment-gate'),
    path('login/', login_options_view, name='login-options'),
    path('login/admin/', login_admin_view, name='login-admin'),
    path('login/patient/', login_patient_view, name='login-patient'),
    path('login/doctor/', login_doctor_view, name='login-doctor'),
    path('logout/', logout_view, name='logout'),
    path('admin/login/', RedirectView.as_view(url='/login/admin/', permanent=False)),
    path('register/', register_options_view, name='register-options'),
    path('register/patient/', register_patient_view, name='register-patient'),
    path('register/doctor/', register_doctor_view, name='register-doctor'),
    path('hms-admin/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin_page_view, name='admin-page'),
    path('admin/billing-history/', admin_billing_history_view, name='admin-billing-history'),
    path('doctor/', doctor_page_view, name='doctor-page'),
    path('doctor/billing/', doctor_billing_view, name='doctor-billing'),
    path('patient/', patient_page_view, name='patient-page'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/prescriptions/', include('prescriptions.urls')),
    path('api/billing/', include('billing.urls')),
]
