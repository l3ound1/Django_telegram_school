from django.shortcuts import render
from Users.models import User,Schedule
from . import teacher_schedule
import Store
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
        if predment in schedule_subjects:
            continue
        else:
            predment_no_teacher.append((predment + " ").title())
    context = {
        'user': user,
        'predment_no_teacher':predment_no_teacher
    }

    return render(request, 'profileStudent/profile.html', context)



def add_teacher(request):
    teachers = []

    if request.method == "POST":
        action = request.POST.get('action')
        button_teacher = request.POST.get('teacher_username')

        if button_teacher:
            username_teacher = request.POST.get("teacher_username")
            result = teacher_schedule.schedule(username_teacher)
            print(result)

    
        else:
            selected_subject = request.POST.get("subjects")
            if selected_subject:
                teachers = User.objects.filter(predment__iexact=selected_subject)
        

    context = {
        'predment_no_teacher': predment_no_teacher,
        "teachers_list": teachers,
    }

    return render(request, 'profileStudent/add_teacher.html', context)

def home_work(request):
    return render(request,'profileStudent/home_work.html')