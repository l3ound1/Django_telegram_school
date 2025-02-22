from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
app_name = "profileStudent"
urlpatterns = [
    path("",views.index,name="prof"),
    path("add_teacher",views.add_teacher,name="add"),
    path("home_work",views.home_work,name="home_work")
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)