import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')
django.setup()

from Users.models import User
from django.contrib.auth.hashers import check_password


#Код отправления: 1 - пользователь зарегистрирован , 2 - пользователь зарегистровался , но не нету предмета , 3  - пользователь не зарегистровался
def check_username(login,password,chat_id_user):
    user = User.objects.get(username__iexact=login)
    if check_password(password,user.password) and user.predment != None:
        if user.status != "admin":
            user.id_t=chat_id_user
            user.save()
        return[1,user.predment,user.status,user.name,user.fullname,chat_id_user]
    elif check_password(password,user.password) and user.predment == None:
        user.id_t=chat_id_user
        user.save()
        return[2,None]
    else:
        return[3]




