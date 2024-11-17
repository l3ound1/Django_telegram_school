from Users.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import sendsms
import datetime
from . import function_course


def index(request):
    return  render(request,'storeshop/index.html')
def categ(request):
    return  render(request,'storeshop/category.html')
def buycategory(request):
    step = request.GET.get("step")
    return render(request,"storeshop/buy.html",context={"step":step})
def course(request):
    step = request.GET.get("step")
    month = request.GET.get("m")
    if request.method == "POST":
        function_course.course_buy(request,step,month)


        return redirect('storeshop:home')



    return render(request, "storeshop/buy_course.html", context={
        "step": step,
        "month": month
    })
def mail_sms(request):
    return  render(request,"storeshop/result.html")