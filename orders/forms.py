import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import ContactMessage, Order

PHONE_RE = re.compile(r'^\+?\d{9,15}$')


def clean_phone_number(value):
    phone = re.sub(r'[\s-]', '', value)
    if not PHONE_RE.match(phone):
        raise forms.ValidationError('Enter a valid phone number, e.g. 0712345678 or +254712345678.')
    return phone


class BootstrapFormMixin:
    """Adds Bootstrap's form-control / form-select class to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css)


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label='Username or email')

    def clean(self):
        # Allow logging in with an email address as well as a username.
        username = self.cleaned_data.get('username')
        if username and '@' in username:
            user = User.objects.filter(email__iexact=username).first()
            if user:
                self.cleaned_data['username'] = user.username
        return super().clean()


class OrderForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'location', 'delivery_address', 'phone', 'delivery_date', 'notes']
        labels = {'quantity': 'Quantity (litres)'}
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Anything the rider should know (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_phone(self):
        return clean_phone_number(self.cleaned_data['phone'])

    def clean_delivery_date(self):
        date = self.cleaned_data['delivery_date']
        if date < timezone.localdate():
            raise forms.ValidationError('Delivery date cannot be in the past.')
        return date


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return clean_phone_number(phone) if phone else phone
