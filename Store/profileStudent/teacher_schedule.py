from Users.models import User,Schedule
from . import Schedule_dict


def schedule(username):
    teacher = User.objects.get(username__iexact=username)


    teacher_schedule = teacher.schedule.all()



    busy_times = teacher_schedule.values_list('time', flat=True)
    free_times = {}

    for key, value in Schedule_dict.SCHEDULE_old.items():
        day = value["day"]
        time = value["time"]
        if key not in busy_times:
            if day not in free_times:
                free_times[day] = []
            free_times[day].append(time)

    if free_times:
        return free_times
    else:
        return "Учитель занят в течение всей недели"


def get_teacher(username):
    return User.objects.get(username__iexact=username)

def get_all_free_times():
    return {
        "Понедельник": ["1 = 8:00 - 10:00", "2 = 10:15 - 12:15", "3 = 12:30 - 14:00", "4 = 14:15 - 16:00"],
        "Вторник": ["5 = 8:00 - 10:00", "6 = 10:15 - 12:15", "7 = 14:15 - 16:00", "8 = 16:15 - 18:00"],
        "Среда": ["9 = 8:00 - 10:00", "10 = 10:15 - 12:15", "11 = 12:30 - 14:00", "12 = 14:15 - 16:00"],
        "Четверг": ["13 = 8:00 - 10:00", "14 = 10:15 - 12:15", "15 = 12:30 - 14:00", "16 = 14:15 - 16:00"],
        "Пятница": ["17 = 8:00 - 10:00", "18 = 10:15 - 12:15", "19 = 12:30 - 14:00", "20 = 14:15 - 16:00"],
        "Суббота": ["21 = 8:00 - 10:00", "22 = 10:15 - 12:15", "23 = 12:30 - 14:00", "24 = 14:15 - 16:00"]
    }