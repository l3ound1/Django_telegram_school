import sqlite3
from django.contrib.auth.hashers import check_password
from django.db.models.functions import Length

from Users.models import User, Schedule
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')


django.setup()




#1 - Пользователь авторизовался ,но нету выбор профиля 2 - Пользователь авторизовался есть профиль 3 - Не верный логин или пароль
def check(login,password,check_predmet =0):
    if check_predmet == 1:
        predmet = predment_list(login,check_predmet)

    try:
        user = User.objects.get(username__iexact=login)
        predmet = user.predment
    except:
        return [3,"",""]
    if check_predmet == 1:
        predmet = predment_list(login, check_predmet)
    if check_password(password, user.password) == True and user.profile == None:
        return [1,user.name,user.fullname,login,user.schedule,user.profile,user.photo_teacher,predmet,user.id_t]
    if check_password(password,user.password) == True and user.profile != None:
        list_predment = predment_list(login,check_predmet = 1)
        if user.schedule.annotate(len=Length('time')) != len(list_predment):
            return [2, user.name, user.fullname, login, None, user.profile, user.photo_teacher, predmet,user.id_t]
        else:
            return [2, user.name, user.fullname, login, user.schedule.time, user.profile, user.photo_teacher, predmet]
    if password == " ":
         return [1, user.name, user.fullname, login, user.schedule, user.profile, user.photo_teacher, predmet]

    else:
        return [3,user.name,user.fullname]

#сохранение профиля
def student_teacher(login,prof):

        user = User.objects.get(username__iexact=login)

        user.profile = prof
        user.save()

#предметы и даты
def predment_list(login,check_predmet = 0):
    list_messsage = []
    user = User.objects.get(username__iexact=login)
    if user.predment is None:
        return []
    else:
        predment = user.predment
        predment_list = [word + " "for word in predment.split(" ") if word]
        if check_predmet == 1:
            return predment_list
        else:
            data = user.timecourse
            data_list = [word for word in data.split(" ") if word]
            i = 0
            j = 0
            while i < len(predment_list) and j < len(data_list):
                if int(data_list[j]) == 3:
                    list_messsage.append(list_messsage.append(f"{predment_list[i]} - {data_list[j]} месяца"))
                elif int(data_list[j]) == 9:
                    list_messsage.append(list_messsage.append(f"{predment_list[i]} - {data_list[j]} месяцов"))
                else:
                    list_messsage.append(f"{predment_list[i]} - {data_list[j]} месяц")
                i+=1
                j+=1
            for k in range(len(list_messsage) - 1 ):
                if list_messsage[k] == None:
                    list_messsage.pop(k)

    return  list_messsage

#оценки
def evaluations(login):
    user = User.objects.get(username__iexact = login)
    list_evaluations = user.evaluations
    if list_evaluations == None:
        return ["У вас нет оценок"]
    average = 0
    for i in range(len(list_evaluations)):
        if list_evaluations[i] == " ":
            continue
        average += int(list_evaluations[i])
    average /= len(list_evaluations)
    return [list_evaluations,average]

#сохранение фото
def save_photo(message,login,bot):
    user = User.objects.get(username__iexact=login)
    try:
        file_into = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        download_file = bot.download_file(file_into.file_path)
        src = './photo/' + file_into.file_path.replace("photos/", f"{user.name} {user.patronymic}")
        if not os.path.exists('./photo/'):
            os.makedirs('./photo/')
        with open(src, "wb") as new_file:
            new_file.write(download_file)
            new_file.close()
        user.photo_teacher = src
        user.save()
        return ["Ваше фото сохранено",user.name, user.fullname,user.patronymic,login,user.schedule,user.profile,user.photo_teacher,user.predment]
    except:
        return "Ваше фото не сохранено"

#Сохранение предметов учителей
def save_teacher_predment(login, predment):
    try:
        user = User.objects.get(username__iexact=login)
        if user.predment:
            user.predment += f"{predment} "
        else:
            user.predment = f"{predment} "
        user.save()
        return [user.name, user.fullname, user.patronymic, login, user.schedule, user.profile, user.photo_teacher, user.predment]
    except Exception as e:
        print(f"Ошибка при сохранении предмета учителя: {e}")
        return []

#Список учителей
def teacher_list(predment):
    techears = User.objects.filter(predment__iexact=predment,profile__iexact="teacher")
    return techears



#Реализация свободного времени учителя
def check_time_teachers(teacher_username):
    teacher = User.objects.filter(username__iexact=teacher_username).first()
    if not teacher:
            return "Учитель не найден"
    else:
        teacher_schedule = teacher.schedule.all()

        if not teacher_schedule:
            free_time = get_all_free_times()
            return "\n".join(
                [f"{day}: {', '.join(times)}" for day, times in free_time.items()]) + "\nНажмите на кнопку <<выбрать>>"

        all_schedule = {
            "Понедельник": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                            {"time": "12:30 - 14:00", "number": 3}, {"time": "14:15 - 16:00", "number": 4}],
            "Вторник": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                        {"time": "14:15 - 16:00", "number": 3}, {"time": "16:15 - 18:00", "number": 4}],
            "Среда": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                      {"time": "12:30 - 14:00", "number": 3}, {"time": "14:15 - 16:00", "number": 4}],
            "Четверг": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                        {"time": "12:30 - 14:00", "number": 3}, {"time": "14:15 - 16:00", "number": 4}],
            "Пятница": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                        {"time": "12:30 - 14:00", "number": 3}, {"time": "14:15 - 16:00", "number": 4}],
            "Суббота": [{"time": "8:00 - 10:00", "number": 1}, {"time": "10:15 - 12:15", "number": 2},
                        {"time": "12:30 - 14:00", "number": 3}, {"time": "14:15 - 16:00", "number": 4}],
        }

        free_times = {}

        for day, periods in all_schedule.items():
            free_periods = []
            teacher_day_schedule = teacher_schedule.filter(time__icontains=day)

            for period in periods:
                if not teacher_day_schedule.filter(time=period["time"]).exists():
                    free_periods.append(period["time"])

            if free_periods:
                free_times[day] = free_periods

        if free_times:
            return "\n".join([f"{day}: {', '.join(times)}" for day, times in free_times.items()])
        else:
            return "Учитель занят в течение всей недели"


def get_all_free_times():
    return {
        "Понедельник": ["1 = 8:00 - 10:00", "2 = 10:15 - 12:15", "3 = 12:30 - 14:00", "4 = 14:15 - 16:00"],
        "Вторник": ["5 = 8:00 - 10:00", "6 = 10:15 - 12:15", "7 = 14:15 - 16:00", "8 = 16:15 - 18:00"],
        "Среда": ["9 = 8:00 - 10:00", "10 = 10:15 - 12:15", "11 = 12:30 - 14:00", "12 = 14:15 - 16:00"],
        "Четверг": ["13 = 8:00 - 10:00", "14 = 10:15 - 12:15", "15 = 12:30 - 14:00", "16 = 14:15 - 16:00"],
        "Пятница": ["17 = 8:00 - 10:00", "18 = 10:15 - 12:15", "19 = 12:30 - 14:00", "20 = 14:15 - 16:00"],
        "Суббота": ["21 = 8:00 - 10:00", "22 = 10:15 - 12:15", "23 = 12:30 - 14:00", "24 = 14:15 - 16:00"]
    }


def result_time(time, teacher_fullname, login, subject_name):
    time_teachers = get_all_free_times()

    for day in time_teachers:
        for value in time_teachers[day]:
            if time in value:
                user = User.objects.get(username__iexact=login)
                schedule = Schedule.objects.create(time=time, teacher=teacher_fullname, subject=subject_name)
                user.schedule.add(schedule)
                user.save()
                return value

    return "Не найдено\nНапишите заново!"

def check_predment(login):
    user = User.objects.filter(username__iexact=login).first()
    if user:
        predments = [schedule.predment for schedule in user.schedule.all()]
        return predments
    else:
        return []


#для сохранения данных
def save_data(login,data):
    user = User.objects.get(username__iexact = login)
    user.id_t = data
    user.save()