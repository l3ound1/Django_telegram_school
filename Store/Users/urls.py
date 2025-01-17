from django.contrib.auth.views import LogoutView
from django.urls import path, include

from . import views
app_name = "Users"
urlpatterns = [
    path("login/",views.UsersLogin.as_view(),name = "login"),
    path("logout/",LogoutView.as_view(),name = "logout"),
    path("register/", views.Users_Add.as_view(), name="register"),
    
]