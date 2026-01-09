"""
Forms for fleet management.
"""
from django import forms
from .models import Vehicle, Route, RoutePoint, Trip, FuelRecord


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

