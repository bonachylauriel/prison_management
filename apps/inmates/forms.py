from django import forms
from .models import Inmate, Detention, Visit
from datetime import timedelta


class InmateForm(forms.ModelForm):
    class Meta:
        model = Inmate
        fields = ['registration_number', 'first_name', 'last_name', 'date_of_birth',
                 'gender', 'photo', 'current_prison', 'admission_date', 'release_date',
                 'health_status', 'is_recidivist', 'crime_description']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'release_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DetentionForm(forms.ModelForm):
    class Meta:
        model = Detention
        fields = ['inmate', 'warrant_pdf', 'start_date', 'end_date', 'magistrate']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class VisitForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local' ,
                'class': 'form-control'
            }
        ) ,
        label="Date et heure de la visite"
    )

    duration = forms.DurationField(
        initial=timedelta(hours=1) ,
        widget=forms.Select(
            choices=[
                (timedelta(minutes=30) , '30 minutes') ,
                (timedelta(hours=1) , '1 heure') ,
                (timedelta(minutes=90) , '1 heure 30') ,
                (timedelta(hours=2) , '2 heures') ,
            ] ,
            attrs={'class': 'form-control'}
        ) ,
        label="Durée de la visite"
    )

    class Meta:
        model = Visit
        fields = ['visitor_name' , 'visitor_id_number' , 'visitor_phone' ,
                  'visitor_relation' , 'date' , 'duration' , 'notes']
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control'}) ,
            'visitor_id_number': forms.TextInput(attrs={'class': 'form-control'}) ,
            'visitor_phone': forms.TextInput(attrs={'class': 'form-control'}) ,
            'visitor_relation': forms.Select(attrs={'class': 'form-control'}) ,
            'notes': forms.Textarea(attrs={'class': 'form-control' , 'rows': 3}) ,
        }


class VisitApprovalForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['status' , 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}) ,
            'notes': forms.Textarea(attrs={'class': 'form-control' , 'rows': 3}) ,
        }
