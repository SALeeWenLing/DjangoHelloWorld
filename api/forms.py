from functools import total_ordering

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum

from . import models
from .models import Task, DevelopmentTag, Sprint, TimeLog
from .models import ThemeSettings, THEME_CHOICES
from .models import ModeSettings, MODE_CHOICES

User = get_user_model()


class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model = ThemeSettings
        fields = ['theme']
        widgets = {
            'theme': forms.Select(choices=THEME_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(ThemeSettingsForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ModeSettingsForm(forms.ModelForm):
    class Meta:
        model = ModeSettings
        fields = ['mode']
        widgets = {
            'mode': forms.Select(choices=MODE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(ModeSettingsForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'         


STORY_POINTS = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10,'10'),
]

class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['sprint_name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'id': 'startDate'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'id': 'endDate'}),
            'activated': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise ValidationError('End date must be at least one day after the start date.')

        return cleaned_data

class CreateNewList(forms.ModelForm):
    story_point = forms.ChoiceField(choices=STORY_POINTS)
    task_name = forms.CharField(label='Task')
    development_tag = forms.ModelMultipleChoiceField(
        queryset=DevelopmentTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Task
        fields = ['task_name', 'description', 'priority', 'assignee', 'task_type', 'story_point', 'task_stage', 'status', 'development_tag']
        widgets = {
            'done': forms.CheckboxInput(),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),  # Customize the size of the textarea
        }

    def __init__(self, *args, **kwargs):
        super(CreateNewList, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class RegisterForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ["username", "email", "password1", "password2"]


class AdminUserChangeForm(UserChangeForm):
    reset_password = forms.BooleanField(
        required=False,
        label="Reset Password to 'password12345'"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'is_superuser', 'reset_password')

    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['is_superuser'].label = "Admin"

        # Remove the password field
        if 'password' in self.fields:
            del self.fields['password']

    def save(self, commit=True):
        user = super(AdminUserChangeForm, self).save(commit=False)
        if self.cleaned_data.get('reset_password'):
            user.set_password('password12345')
        if commit:
            user.save()
        return user



class StaffUserChangeForm(UserChangeForm):
    old_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="Old Password"
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="New Password"
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="Confirm New Password"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(StaffUserChangeForm, self).__init__(*args, **kwargs)
        # Remove the password field
        if 'password' in self.fields:
            del self.fields['password']

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 or new_password2:
            if not old_password:
                raise ValidationError("Old password is required to set a new password.")
            if new_password1 != new_password2:
                raise ValidationError("The new passwords do not match.")
            if not self.instance.check_password(old_password):
                raise ValidationError("The old password is incorrect.")
            # Validate the new password using Django's built-in validators
            validate_password(new_password1, self.instance)

        return cleaned_data

    def save(self, commit=True):
        user = super(StaffUserChangeForm, self).save(commit=False)
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            user.set_password(new_password1)
        if commit:
            user.save()
        return user

class TimeLogForm(forms.ModelForm):
    time_spent = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), min_value=0)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    total_time_spent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)

    class Meta:
        model = TimeLog
        fields = ['time_spent', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        user = kwargs.pop('user')
        super(TimeLogForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.instance.task = task
        self.instance.user = user
        related_timelogs = TimeLog.objects.filter(task=self.instance.task)
        total_time = 0
        for log in related_timelogs:
            total_time += log.time_spent
        # TODO: Value here is never updated in save
        self.fields['total_time_spent'].initial = total_time


    def save(self, commit=True):
        timelog = super(TimeLogForm, self).save(commit=False)
        if commit:
            timelog.save()
            total_time = 0
            if self.instance and hasattr(self.instance, 'task') and self.instance.task:
                related_timelogs = TimeLog.objects.filter(task=self.instance.task)
                for log in related_timelogs:
                    total_time += log.time_spent                # TODO: Correct value, but not updating in form
                self.fields['total_time_spent'].initial = total_time

            self.save_m2m()
        return timelog


