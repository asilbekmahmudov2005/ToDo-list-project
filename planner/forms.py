from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'date', 
            'start_time', 'end_time', 'duration', 
            'priority', 'category', 'is_completed'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Masalan: Dasturlash asoslarini o‘rganish',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3, 
                'placeholder': 'Vazifa haqida batafsil maʼlumot...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input', 
                'type': 'date',
                'required': True
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input', 
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input', 
                'type': 'time'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Masalan: 45 (daqiqa)',
                'min': '0'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            raise ValidationError({
                'end_time': "Tugash vaqti boshlanish vaqtidan kechroq bo‘lishi kerak."
            })
        return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Parol kiriting'
        }),
        label="Parol",
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Parolni qayta kiriting'
        }),
        label="Parolni tasdiqlang"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Foydalanuvchi nomi (login)'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Ismingiz'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Elektron pochta manzilingiz'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Bu foydalanuvchi nomi allaqachon band.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError({
                'confirm_password': "Kiritilgan parollar bir-biriga mos kelmadi."
            })
        return cleaned_data
