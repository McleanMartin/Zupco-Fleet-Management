"""
Forms for fleet management.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from apps.core.roles import DRIVER, assign_role
from .models import Vehicle, Route, RoutePoint, Trip, FuelRecord, Driver


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['registration', 'make', 'model', 'year', 'capacity', 'status']
        widgets = {
            'registration': forms.TextInput(attrs={'class': 'form-input'}),
            'make': forms.TextInput(attrs={'class': 'form-input'}),
            'model': forms.TextInput(attrs={'class': 'form-input'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class RoutePointForm(forms.ModelForm):
    class Meta:
        model = RoutePoint
        fields = ['route', 'sequence', 'name', 'latitude', 'longitude', 'scheduled_time']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.000001'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
        }


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['vehicle', 'route', 'scheduled_start', 'scheduled_end', 'status']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_start': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'scheduled_end': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = ['vehicle', 'date', 'transaction_type', 'fuel_type', 'quantity', 'cost', 'odometer_reading', 'notes']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'transaction_type': forms.Select(attrs={'class': 'form-input'}),
            'fuel_type': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }



class DriverForm(forms.ModelForm):
    """Create or edit a driver, optionally with a login account in the Driver role."""

    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'autocomplete': 'off'}),
        help_text="Leave blank if the driver does not need to log in",
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'autocomplete': 'new-password'}),
    )
    password_confirm = forms.CharField(
        label='Confirm password',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'autocomplete': 'new-password'}),
    )

    class Meta:
        model = Driver
        fields = [
            'first_name', 'last_name', 'employee_number', 'phone', 'national_id',
            'license_number', 'license_class', 'license_expiry', 'assigned_vehicle', 'status',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'employee_number': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'national_id': forms.TextInput(attrs={'class': 'form-input'}),
            'license_number': forms.TextInput(attrs={'class': 'form-input'}),
            'license_class': forms.TextInput(attrs={'class': 'form-input'}),
            'license_expiry': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}, format='%Y-%m-%d'),
            'assigned_vehicle': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['username'].help_text = ''
            self.fields['password'].help_text = 'Leave blank to keep the current password.'

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if username:
            existing = User.objects.filter(username=username)
            if self.instance.user:
                existing = existing.exclude(pk=self.instance.user.pk)
            if existing.exists():
                raise forms.ValidationError('Username already exists.')
        elif self.instance.user:
            raise forms.ValidationError('Username cannot be removed from an existing account.')
        return username

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        password = cleaned.get('password')
        creating_account = username and not self.instance.user
        if creating_account and not password:
            self.add_error('password', 'Password is required to create a login account.')
        if password:
            if not username:
                self.add_error('username', 'Username is required when setting a password.')
            elif password != cleaned.get('password_confirm'):
                self.add_error('password_confirm', 'Passwords do not match.')
            else:
                try:
                    validate_password(password, self.instance.user)
                except forms.ValidationError as e:
                    self.add_error('password', e)
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        driver = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username:
            user = driver.user or User(is_active=True)
            user.username = username
            user.first_name = driver.first_name
            user.last_name = driver.last_name
            user.is_active = driver.status != 'inactive'
            if password:
                user.set_password(password)
            user.save()
            if driver.user is None:
                assign_role(user, DRIVER)
            driver.user = user

        driver.save()
        return driver
