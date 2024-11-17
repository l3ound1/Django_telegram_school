from  django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class User_Add(UserCreationForm):
    name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'form-input'}))
    fullname = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-input'}))
    patronymic = forms.CharField(label="Отчество", widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = get_user_model()
        fields = ['username','email',"name","fullname","patronymic",'password1', 'password2']
        labels = {
            "email":"Е-майл",
            "username":"Имя пользователя"
        }
    def clean_email(self):
        cd = self.cleaned_data["email"]
        if User.objects.filter(email = cd).exists():
            raise forms.ValidationError("Такой Е-майл уже есть")
        return cd

class Login_Users(AuthenticationForm):
    username = forms.CharField(label='Логин пользователя', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
