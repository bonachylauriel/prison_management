from django import forms
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from .models import (
    User , GuardShift , GuardSpecialization , GuardCertification ,
    TeamUnit , Schedule , IncidentReport
)


class GuardCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username' , 'first_name' , 'last_name' , 'email' , 'phone' ,
                  'badge_number' , 'date_of_birth' , 'address' , 'photo' ,
                  'rank' , 'prison' , 'hire_date')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}) ,
            'hire_date': forms.DateInput(attrs={'type': 'date'}) ,
        }

class GuardProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'photo', 'phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class GuardUpdateForm(UserChangeForm):
    password = None  # Exclure le champ password du formulaire

    class Meta:
        model = User
        fields = ('first_name' , 'last_name' , 'email' , 'phone' ,
                  'address' , 'photo' , 'rank' , 'prison' , 'current_team')


class TeamUnitForm(forms.ModelForm):
    class Meta:
        model = TeamUnit
        fields = ['name' , 'leader' , 'members' , 'prison' , 'is_active']
        widgets = {
            'members': forms.CheckboxSelectMultiple() ,
        }

    def __init__(self , *args , **kwargs):
        prison = kwargs.pop('prison' , None)
        super().__init__(*args , **kwargs)
        if prison:
            self.fields['leader'].queryset = User.objects.filter(prison=prison)
            self.fields['members'].queryset = User.objects.filter(prison=prison)

    def clean(self):
        cleaned_data = super().clean()
        leader = cleaned_data.get('leader')
        members = cleaned_data.get('members')

        if leader and members and leader not in members:
            # Ajouter automatiquement le leader aux membres
            if isinstance(members , list):
                members.append(leader)
            else:
                members = list(members) + [leader]
            cleaned_data['members'] = members

        return cleaned_data


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['guard' , 'team' , 'start_date' , 'end_date' ,
                  'rotation_pattern' , 'notes' , 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}) ,
            'end_date': forms.DateInput(attrs={'type': 'date'}) ,
        }

    def __init__(self , *args , **kwargs):
        prison = kwargs.pop('prison' , None)
        super().__init__(*args , **kwargs)
        if prison:
            self.fields['guard'].queryset = User.objects.filter(prison=prison)
            self.fields['team'].queryset = TeamUnit.objects.filter(prison=prison)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        guard = cleaned_data.get('guard')

        if start_date and end_date and guard:
            if start_date > end_date:
                raise forms.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

            # Vérifier les chevauchements de planning
            overlapping = Schedule.objects.filter(
                guard=guard ,
                start_date__lte=end_date ,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if overlapping:
                raise forms.ValidationError(
                    "Ce planning chevauche un planning existant pour ce garde."
                )

        return cleaned_data


class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['title' , 'incident_date' , 'location' , 'severity' ,
                  'description' , 'involved_inmates' , 'involved_guards' ,
                  'witnesses' , 'immediate_action' , 'follow_up_action' ,
                  'status' , 'attachments']
        widgets = {
            'incident_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ) ,
            'involved_inmates': forms.SelectMultiple(attrs={'class': 'select2'}) ,
            'involved_guards': forms.SelectMultiple(attrs={'class': 'select2'}) ,
            'witnesses': forms.SelectMultiple(attrs={'class': 'select2'}) ,
            'description': forms.Textarea(attrs={'rows': 4}) ,
            'immediate_action': forms.Textarea(attrs={'rows': 3}) ,
            'follow_up_action': forms.Textarea(attrs={'rows': 3}) ,
        }

    def __init__(self , *args , **kwargs):
        prison = kwargs.pop('prison' , None)
        super().__init__(*args , **kwargs)
        if prison:
            self.fields['involved_guards'].queryset = User.objects.filter(prison=prison)
            self.fields['witnesses'].queryset = User.objects.filter(prison=prison)
            self.fields['involved_inmates'].queryset = prison.inmates.all()


class GuardShiftForm(forms.ModelForm):
    class Meta:
        model = GuardShift
        fields = ['guard' , 'start_time' , 'end_time' , 'area' , 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ) ,
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ) ,
            'notes': forms.Textarea(attrs={'rows': 3}) ,
        }

    def __init__(self , *args , **kwargs):
        prison = kwargs.pop('prison' , None)
        super().__init__(*args , **kwargs)
        if prison:
            self.fields['guard'].queryset = User.objects.filter(prison=prison)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError(
                    "L'heure de fin doit être postérieure à l'heure de début."
                )

        return cleaned_data