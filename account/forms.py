from django.contrib.auth.forms import UserCreationForm
from django.forms import widgets
from django.contrib.auth.models import User
from django import forms



class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        self.fields['username'] = forms.CharField(
            widget = widgets.TextInput(
                attrs={'placeholder': "Username", "class": "form-control"},
            ),
            label = 'Никнейм',
        )

        self.fields['email'] = forms.CharField(
            widget = widgets.EmailInput(
                attrs={'placeholder': "Email", "class": "form-control"},
            ),
            label = 'Email',
        )
        
        self.fields['password1'] = forms.CharField(
            widget = widgets.PasswordInput(
                attrs={'placeholder': "Пароль", "class": "form-control"},
            ),
            label = 'Пароль',
        )
        
        self.fields['password2'] = forms.CharField(
            widget = widgets.PasswordInput(
                attrs={'placeholder': "Повторить пароль", "class": "form-control"},
            ),
            label = 'Повторить пароль',
        )
        
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )