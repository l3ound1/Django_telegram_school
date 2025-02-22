from django.shortcuts import render
from Users.models import User
# Create your views here.

predment_no_teacher = []
def index(request):
    predment_no_teacher.clear()
    user = request.user
    predment_list = list(set([subject.strip().lower() for subject in user.predment.split() if subject.strip()]))
    schedule = user.schedule.all()
    schedule_subjects = [s.subject.strip().lower() for s in schedule if s.subject.strip()]
    schedule_subjects = list(set(schedule_subjects))
    for predment in predment_list:
        if predment in  schedule_subjects:
            continue
        else:
            predment_no_teacher.append((predment+" ").title())
    context = {
        'user': user,
        'predment_no_teacher':predment_no_teacher
    }

    return render(request, 'profileStudent/profile.html', context)


def add_teacher(request):
    
    context1 = {
        "predment_list":predment_no_teacher, 
    }
    if request.method == "POST":
        result = request.POST["subjects"].title()
        teachers = User.objects.all().filter(predment=result,profile="teacher")
        print(teachers)
        for i in teachers:
            print(i.name)
        context1["teachers_list"] = teachers
        

    return render(request, 'profileStudent/add_teacher.html',context1)