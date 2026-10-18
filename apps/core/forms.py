"""
Forms for user management.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .roles import ROLE_CHOICES, assign_role, get_role


class UserForm(forms.ModelForm):
    """Create or edit a user and assign their role."""

    role = forms.ChoiceField(
        choices=[('', 'No role')] + ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Determines what the user can see and do",
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
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_new = self.instance.pk is None
        if not self.is_new:
            self.fields['role'].initial = get_role(self.instance)
            self.fields['password'].help_text = 'Leave blank to keep the current password.'
        # Only superusers may grant superuser status.
        if not (request_user and request_user.is_superuser):
            del self.fields['is_superuser']

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        if self.is_new and not password:
            self.add_error('password', 'Password is required.')
        if password:
            if password != cleaned.get('password_confirm'):
                self.add_error('password_confirm', 'Passwords do not match.')
            else:
                try:
                    validate_password(password, self.instance)
                except forms.ValidationError as e:
                    self.add_error('password', e)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            assign_role(user, self.cleaned_data.get('role'))
        return user
