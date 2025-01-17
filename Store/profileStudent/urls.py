from django.urls import path, include

from . import views
app_name = "profileStudent"
urlpatterns = [
    path("",views.index,name="prof")
    
]