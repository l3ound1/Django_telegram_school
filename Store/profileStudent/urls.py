from django.urls import path, include

from . import views
app_name = "profileStudent"
urlpatterns = [
    path("",views.index,name="prof"),
    path("add_teacher",views.add_teacher,name="add")
    
]