from . import Schedule_dict
from Users.models import Schedule
def Add(student,teacher,selected_time):
    selected_time = selected_time.split(" ")
    key_time = 0
    for key,value in Schedule_dict.SCHEDULE_old.items():
        day = value["day"]
        time = value["time"]
        if day == selected_time[0] and time == selected_time[1]:
            key_time = key
    
    new_schedule_entry = Schedule.objects.create(
        time= str(key_time),
        teacher=teacher.fullname,
        subject=teacher.predment[:-1],
        id_student=str(student.id),
        id_teacher=str(teacher.id)
    )


    student.schedule.add(new_schedule_entry)