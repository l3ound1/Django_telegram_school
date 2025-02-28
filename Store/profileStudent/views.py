from django.shortcuts import render, redirect
from Users.models import User,Schedule
from . import teacher_schedule
from . import add_teacher_function
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
    result = {}
    context = {} 

    if request.method == "POST":
        action = request.POST.get('action')
        button_teacher = request.POST.get('teacher_username')
        сonfirmation_selection = request.POST.get('schedule')

        if button_teacher:
            username_teacher = request.POST.get("teacher_username")
            result = teacher_schedule.schedule(username_teacher)
            selected_teacher = teacher_schedule.get_teacher(username_teacher)
            request.session['selected_teacher'] = username_teacher
            context["selected_teacher"] = selected_teacher
        elif сonfirmation_selection:
            user = User.objects.get(username=request.user.username)
            time = request.POST.get("available_times")
            username_teacher_session = request.session.get("selected_teacher")
            selected_teacher = User.objects.get(username__iexact=username_teacher_session)
            result = add_teacher_function.Add(student=user,teacher=selected_teacher,selected_time=time)
            return redirect('profileStudent:prof')
        else:
            selected_subject = request.POST.get("subjects")
            if selected_subject:
                teachers = User.objects.filter(predment__iexact=selected_subject)

    context.update({  
        'predment_no_teacher': predment_no_teacher,
        "teachers_list": teachers,
        "free_time_teacher": result,
        "selected_teacher": context.get("selected_teacher", None),
    })

    return render(request, 'profileStudent/add_teacher.html', context)


def home_work(request):
    return render(request,'profileStudent/home_work.html')