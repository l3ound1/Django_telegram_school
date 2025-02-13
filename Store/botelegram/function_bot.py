import datetime
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')
django.setup()

from Users.models import User,Schedule
from django.contrib.auth.hashers import check_password
SCHEDULE = {
    "1": {"day": "Понедельник", "time": "7:30"},
    "2": {"day": "Понедельник", "time": "9:45"},
    "3": {"day": "Понедельник", "time": "12:00"},
    "4": {"day": "Понедельник", "time": "13:45"},
    "5": {"day": "Вторник", "time": "7:30"},
    "6": {"day": "Вторник", "time": "9:45"},
    "7": {"day": "Вторник", "time": "13:45"},
    "8": {"day": "Вторник", "time": "15:45"},
    "9": {"day": "Среда", "time": "7:30"},
    "10": {"day": "Среда", "time": "9:45"},
    "11": {"day": "Среда", "time": "12:00"},
    "12": {"day": "Среда", "time": "13:45"},
    "13": {"day": "Четверг", "time": "7:30"},
    "14": {"day": "Четверг", "time": "9:45"},
    "15": {"day": "Четверг", "time": "12:00"},
    "16": {"day": "Четверг", "time": "13:45"},
    "17": {"day": "Пятница", "time": "7:30"},
    "18": {"day": "Пятница", "time": "9:45"},
    "19": {"day": "Пятница", "time": "12:00"},
    "20": {"day": "Пятница", "time": "13:45"},
    "21": {"day": "Суббота", "time": "7:30"},
    "22": {"day": "Суббота", "time": "9:45"},
    "23": {"day": "Суббота", "time": "12:00"},
    "24": {"day": "Суббота", "time": "13:45"},
}
SCHEDULE_old = {
    "1": {"day": "Понедельник", "time": "8:00"},
    "2": {"day": "Понедельник", "time": "10:15"},
    "3": {"day": "Понедельник", "time": "12:30"},
    "4": {"day": "Понедельник", "time": "14:15"},
    "5": {"day": "Вторник", "time": "8:00"},
    "6": {"day": "Вторник", "time": "10:15"},
    "7": {"day": "Вторник", "time": "14:15"},
    "8": {"day": "Вторник", "time": "16:15"},
    "9": {"day": "Среда", "time": "8:00"},
    "10": {"day": "Среда", "time": "10:15"},
    "11": {"day": "Среда", "time": "12:30"},
    "12": {"day": "Среда", "time": "14:15"},
    "13": {"day": "Четверг", "time": "8:00"},
    "14": {"day": "Четверг", "time": "10:15"},
    "15": {"day": "Четверг", "time": "12:30"},
    "16": {"day": "Четверг", "time": "14:15"},
    "17": {"day": "Пятница", "time": "8:00"},
    "18": {"day": "Пятница", "time": "10:15"},
    "19": {"day": "Пятница", "time": "12:30"},
    "20": {"day": "Пятница", "time": "14:15"},
    "21": {"day": "Суббота", "time": "8:00"},
    "22": {"day": "Суббота", "time": "10:15"},
    "23": {"day": "Суббота", "time": "12:30"},
    "24": {"day": "Суббота", "time": "14:15"},
} 

#Код отправления: 1 - пользователь зарегистрирован , 2 - пользователь зарегистровался , но не нету предмета , 3  - пользователь не зарегистровался
def check_username(login,password,chat_id_user):
    if login[0] =="/":
        return[3]
    user = User.objects.get(username__iexact=login)
    if check_password(password,user.password) and user.predment != None:
        if user.status != "admin":
            user.id_t=chat_id_user
            user.save()
        return[1,user.predment,user.status,user.name,user.fullname,chat_id_user,user.profile]
    elif check_password(password,user.password) and user.predment == None:
        user.id_t=chat_id_user
        user.save()
        return[2,None]
    else:
        return[3]
def check_predment(login, day_of_week):
    user = User.objects.filter(username__iexact=login).first()
    
    if user:
        for schedule_item in user.schedule.all():
            if SCHEDULE[schedule_item.time]["day"] == day_of_week:
                return [
                    SCHEDULE_old[schedule_item.time]["time"],
                    SCHEDULE[schedule_item.time]["time"],
                    schedule_item.subject
                ]
    return None


def check_teacher_schedule_with_students(teacher_login, day_of_week):
    teacher = User.objects.get(username__iexact=teacher_login, profile="teacher")
    result = []

    if teacher:
        shc = Schedule.objects.filter(id_teacher=teacher.id)
        for schedule_item in shc:
            id_student = schedule_item.id_student
            username_student = User.objects.get(id=id_student)
            if SCHEDULE[schedule_item.time]["day"] == day_of_week:
                    result.append([
                        SCHEDULE_old[schedule_item.time]["time"],
                        SCHEDULE[schedule_item.time]["time"],
                        username_student
                    ])

    return result if result else None


def get_email(login):
    user  = User.objects.get(username__iexact=login)
    return user.email








