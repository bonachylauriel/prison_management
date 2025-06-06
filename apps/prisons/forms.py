from django import forms
from .models import Prison

class PrisonForm(forms.ModelForm):
    class Meta:
        model = Prison
        fields = ['name', 'province', 'capacity', 'current_population']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.Select(attrs={'class': 'form-control select2'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'current_population': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        current_population = cleaned_data.get('current_population')

        if capacity is not None and current_population is not None:
            if capacity < 0:
                raise forms.ValidationError("La capacité ne peut pas être négative.")
            if current_population < 0:
                raise forms.ValidationError("La population actuelle ne peut pas être négative.")
            if current_population > capacity:
                raise forms.ValidationError("La population actuelle ne peut pas dépasser la capacité.")

        return cleaned_data