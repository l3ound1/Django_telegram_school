from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from Users.forms import User_Add, Login_Users


# Create your views here.


class UsersLogin(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("storeshop:home")
        return super().dispatch(request, *args, **kwargs)
    form_class = Login_Users
    template_name = "Users/login_user.html"
    extra_context = {
        "title":"Авторизация",
        "choice":"Войти"
    }
    def get_success_url(self):
        return  reverse_lazy("storeshop:home")


class Users_Add(CreateView):
    form_class = User_Add
    template_name = "Users/login_user.html"
    extra_context = {
        "title": "Регистрация",
        "choice": "Зарегистрироваться"
    }

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('storeshop:home')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('Users:login')


