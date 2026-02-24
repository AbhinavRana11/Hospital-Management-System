from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardStatsAPIView,
    DoctorViewSet,
    PatientViewSet,
    RegisterAPIView,
    login_admin_view,
    login_doctor_view,
    login_options_view,
    login_patient_view,
    register_doctor_view,
    register_options_view,
    register_patient_view,
)

router = DefaultRouter()
router.register('doctors', DoctorViewSet, basename='doctor')
router.register('patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('login/options/', login_options_view, name='login-options'),
    path('login/admin/', login_admin_view, name='login-admin'),
    path('login/patient/', login_patient_view, name='login-patient'),
    path('login/doctor/', login_doctor_view, name='login-doctor'),
    path('register/options/', register_options_view, name='register-options'),
    path('register/patient/', register_patient_view, name='register-patient'),
    path('register/doctor/', register_doctor_view, name='register-doctor'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('dashboard/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('', include(router.urls)),
]
