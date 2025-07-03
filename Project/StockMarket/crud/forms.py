from django import forms
from django.core.validators import MaxValueValidator
from .models import Stock

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