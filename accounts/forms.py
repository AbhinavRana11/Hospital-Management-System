from django import forms
from django.contrib.auth import get_user_model

from .models import ContactQuery, Doctor
from appointments.models import Appointment

User = get_user_model()


class BaseRegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save_user(self, role):
        full_name = self.cleaned_data['full_name'].strip()
        first_name, last_name = full_name, ''
        if ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        user = User(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


class PatientRegisterForm(BaseRegisterForm):
    dob = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))


class DoctorRegisterForm(BaseRegisterForm):
    specialization = forms.CharField(max_length=120)
    license_number = forms.CharField(max_length=80)

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if Doctor.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError('A doctor with this license number is already registered.')
        return license_number


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ContactQueryForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = ['name', 'age', 'dob', 'address', 'problem']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'problem': forms.Textarea(attrs={'rows': 4}),
        }


class AppointmentBookForm(forms.ModelForm):
    specialization = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={
            'placeholder': 'Select specialization...',
            'list': 'specializations'
        }),
        required=True,
        label='Doctor Specialization'
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.select_related('user').filter(user__is_active=True),
        widget=forms.RadioSelect(),
        label='Select Doctor',
        required=True
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your problem...'}),
        }
        labels = {
            'reason': 'Describe Your Problem',
        }
