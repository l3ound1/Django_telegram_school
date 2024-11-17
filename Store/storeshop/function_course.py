from Users.models import User
from . import sendsms

def course_buy(request,step,month):
    user_id = request.GET.get("i")
    user = User.objects.get(id=user_id)
    email = user.email
    user.predment += f"{step}" + " "
    message = f"Привет, мой друг! Ты купил курс по подготовке к ЕГЭ. Предмет: {step}. Переходи в Телеграмм бот, там будет подробное описание твоего обучения."
    user.timecourse += f"{month}" + " "
    user.save()


    sendsms.send_test_email(message, email)