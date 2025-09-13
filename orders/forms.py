from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'phone', 'payment_method']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse complète'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code postal'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone (optionnel)'}),
            'payment_method': forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'address': 'Adresse',
            'postal_code': 'Code postal',
            'city': 'Ville',
            'phone': 'Téléphone',
            'payment_method': 'Mode de paiement',
        }

