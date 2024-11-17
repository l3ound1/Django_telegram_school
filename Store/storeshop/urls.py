from django.urls import path
from . import sendsms
from . import views
app_name = "storeshop"
urlpatterns = [
    path("",views.index,name = "home"),
    path("category",views.categ,name = "category"),
    path("buy",views.buycategory,name = "buy"),
    path("course",views.course,name = "course"),
    path("mailsend",views.mail_sms,name = "result"),

]