import sqlite3
from django.contrib.auth.hashers import check_password
from Users.models import User
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')


django.setup()




#1 - Пользователь авторизовался ,но нету выбор профиля 2 - Пользователь авторизовался есть профиль 3 - Не верный логин или пароль
def check(login,password):
    try:
        user = User.objects.get(username__iexact=login)
    except:
        return [3,"",""]
    if check_password(password, user.password) == True and user.profile == None:
        return [1,user.name,user.fullname,login,user.schedule,user.profile,user.photo_teacher,user.predment]
    if check_password(password,user.password) == True and user.profile != None:
        return [2, user.name, user.fullname, login, user.schedule, user.profile, user.photo_teacher, user.predment]
    if password == " ":
         return [1, user.name, user.fullname, login, user.schedule, user.profile, user.photo_teacher, user.predment]

    else:
        return [3,user.name,user.fullname]

def student_teacher(login,prof):

        user = User.objects.get(username__iexact=login)

        user.profile = prof
        user.save()

def predment_list(login):
    list_messsage = []
    user = User.objects.get(username__iexact=login)
    if user.predment is None:
        return None
    else:
        predment = user.predment
        predment_list = [word for word in predment.split(" ") if word]
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
        for k in range(len(list_messsage) - 1):
            if list_messsage[k] == None:
                list_messsage.pop(k)
    return  list_messsage

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

def save_teacher_predment(login,predment):
    user = User.objects.get(username__iexact = login)
    user.predment = predment + ' '
    if user.save():
        return [1,user.name,user.fullname,login,user.schedule,user.profile,user.photo_teacher,user.predment]
    else:
        return [0,user.name,user.fullname,login,user.schedule,user.profile,user.photo_teacher,user.predment]


def teacher_list(predment):
    techears = User.objects.filter(predment__iexact=predment,profile__iexact="teacher")
    return techears


