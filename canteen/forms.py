from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from .models import Review, PreOrder, PickupSlot

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)], 
                                 attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 
                                           'placeholder': 'Share your experience with this dish...'}),
        }

class PreOrderForm(forms.ModelForm):
    class Meta:
        model = PreOrder
        fields = ['quantity', 'pickup_slot', 'date', 'special_instructions']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'pickup_slot': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                                        'placeholder': 'Any special requests?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to tomorrow
        tomorrow = date.today() + timedelta(days=1)
        self.fields['date'].widget.attrs['min'] = tomorrow.strftime('%Y-%m-%d')
        
        # Set maximum date to 7 days ahead
        max_date = date.today() + timedelta(days=7)
        self.fields['date'].widget.attrs['max'] = max_date.strftime('%Y-%m-%d')
        
        # Only show active pickup slots
        self.fields['pickup_slot'].queryset = PickupSlot.objects.filter(is_active=True)
    
    def clean_date(self):
        selected_date = self.cleaned_data['date']
        tomorrow = date.today() + timedelta(days=1)
        max_date = date.today() + timedelta(days=7)
        
        if selected_date < tomorrow:
            raise forms.ValidationError("Orders must be placed at least one day in advance.")
        
        if selected_date > max_date:
            raise forms.ValidationError("Orders can only be placed up to 7 days in advance.")
        
        return selected_date
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        if quantity > 10:
            raise forms.ValidationError("Maximum quantity per order is 10.")
        return quantity

class DishSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search dishes...'
        })
    )
    
    DISH_TYPE_CHOICES = [
        ('', 'All Types'),
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('beverage', 'Beverages'),
    ]
    
    dish_type = forms.ChoiceField(
        choices=DISH_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    SORT_CHOICES = [
        ('name', 'Name'),
        ('price', 'Price'),
        ('rating', 'Rating'),
    ]
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )