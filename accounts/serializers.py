from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Doctor, Patient

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='DOCTOR'),
        source='user',
        write_only=True,
    )

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'user_id', 'specialization', 'license_number']


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='PATIENT'),
        source='user',
        write_only=True,
    )

    class Meta:
        model = Patient
        fields = ['id', 'user', 'user_id', 'age', 'gender', 'contact_number']
