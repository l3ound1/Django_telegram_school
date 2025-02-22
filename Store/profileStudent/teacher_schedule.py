from Users.models import User,Schedule



                    #                       <!-- Dropdown for available times -->
                    #                       <h3>Доступное время для занятий</h3>
                    #   <select name="available_times" class="form-control">
                    #     {% for slot in available_slots %}
                    #       <option value="{{ slot.time }}">{{ slot.time }} ({{ slot.day }})</option>
                    #     {% empty %}
                    #       <option>Нет доступных временных слотов</option>
                    #     {% endfor %}
                    #   </select>

def schedule(username):
    try:
        teacher = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return "Учитель не найден"

    teacher_schedule = teacher.schedule.all()


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

    busy_times = teacher_schedule.values_list('time', flat=True)
    print(busy_times)
    free_times = []

    for key, value in SCHEDULE_old.items():
        day = value["day"]
        time = value["time"]

        if key not in busy_times:
            free_times.append(f'{{day: "{day}", time: "{time}"}}')

    if free_times:
        return "\n".join(free_times)
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