from django import forms
from django.core.validators import MaxValueValidator
from .models import Stock
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BuyStockForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity'
        })
    )

class SellStockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    
    def __init__(self, *args, **kwargs):
        max_quantity = kwargs.pop('max_quantity', None)
        super().__init__(*args, **kwargs)
        
        if max_quantity:
            self.fields['quantity'].widget.attrs.update({
                'max': max_quantity,
                'class': 'form-control',
                'placeholder': f'Max: {max_quantity}'
            })
            self.fields['quantity'].validators.append(
                MaxValueValidator(max_quantity)
            )

class StockSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search stocks...'
        }),
        required=False
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user