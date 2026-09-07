from django import forms
from django.contrib.auth.models import User


class UserEditForm(forms.ModelForm):
    """Форма редактирования общедоступных данных пользователя."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Придумайте уникальное имя',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email для связи',
            }),
        }
