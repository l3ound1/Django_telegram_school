import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')

django.setup()
from Users.models import User
import telebot
import function_bot

token = "7470312463:AAHyOhDBNgjJdJ_8s7i2sIMPd7p_E-QPRQs"
bot = telebot.TeleBot(token)
users = {}
result = []
user_teacher_or_student = ""
check_index_techer = False


@bot.message_handler(commands=['start'])
def hello_start(message):
    chat_id = message.chat.id
    users[chat_id] = {}
    bot.send_message(chat_id, "Привет! Введи свой логин:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_login)


def save_login(message):
    chat_id = message.chat.id
    login = message.text
    users[chat_id]['login'] = login
    bot.send_message(chat_id, f"Отлично, {login}. Теперь введи свой пароль:")
    bot.register_next_step_handler(message, save_password)


def save_password(message):
    chat_id = message.chat.id
    password = message.text
    users[chat_id]['password'] = password
    result = function_bot.check(login=users[chat_id]['login'], password=password)
    user_teacher_or_student = users[chat_id]["login"]
    if result[0] == 1:
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_teacher = telebot.types.InlineKeyboardButton(text="👩🏻‍🏫 Учитель", callback_data="teacher")
        button_student = telebot.types.InlineKeyboardButton(text="👨🏻‍🎓 Ученик", callback_data="student")
        keyboard.add(button_student, button_teacher)

        bot.send_message(chat_id, f"Здраствуйте,{result[1]} {result[2]}\n"
                                  f"Выбери свой профиль", reply_markup=keyboard)
        if result[-1] == None:
            function_bot.save_data(users[chat_id]['login'],chat_id)
    if result[0] == 2:

        if result[5] == "teacher":
            if result[6] is None:
                bot.send_message(message.chat.id, "Отправьте ваше фото")
            elif result[6] is not None:
                teacher_profile(message=message, res=result)
        else:
            user_profile(message=message, res=result)
        if result[-1] == None:
            function_bot.save_data(users[chat_id]['login'],chat_id)
    if result[0] == 3:
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_teacher = telebot.types.InlineKeyboardButton(text="Заново", callback_data="restart")
        button_restart_password = telebot.types.InlineKeyboardButton(text="Восстановить пароль",
                                                                     callback_data="password_restart",
                                                                     url="http://127.0.0.1:8000/")
        keyboard.add(button_teacher, button_restart_password)
        bot.send_message(chat_id, "Неправильный логин или пароль.", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['teacher', 'student'])
def profile_selection(call):
    result1 = []
    dataprof = ""
    if call.data == 'teacher':
        bot.send_message(call.message.chat.id, "Вы выбрали: Учитель")
        dataprof = "teacher"
    elif call.data == 'student':
        bot.send_message(call.message.chat.id, "Вы выбрали: Ученик")
        dataprof = "student"
    user_login = users[call.message.chat.id]['login']
    function_bot.student_teacher(user_login, prof=dataprof)
    result1 = function_bot.check(login=users[call.message.chat.id]['login'], password=" ")
    if dataprof == "student":
        user_profile(message=call.message, res=result1)
    if dataprof == "teacher" and result1[6] is not None:
        teacher_profile(message=call.message, res=result1)
    elif dataprof == "teacher" and result1[6] is None:
        bot.send_message(call.message.chat.id, "Отправьте ваше фото")


def teacher_profile(message, res):
    chat_id = message.chat.id
    if type(res[0]) == int and res[len(res) - 1] is not None:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Расписание на неделю ", callback_data="week")
        btn2 = telebot.types.InlineKeyboardButton(text="Домашние задание", callback_data="home_work")
        btn3 = telebot.types.InlineKeyboardButton(text="Оценки", callback_data="evaluations")
        keyboard.add(btn1, btn2, btn3)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте, {res[1]} {res[2]}.\n", reply_markup=keyboard)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Георафия", callback_data="Георафия")
        btn2 = telebot.types.InlineKeyboardButton(text="Физика", callback_data="Физика")
        btn3 = telebot.types.InlineKeyboardButton(text="Математика", callback_data="Математика")
        btn4 = telebot.types.InlineKeyboardButton(text="Информатика", callback_data="Информатика")
        btn5 = telebot.types.InlineKeyboardButton(text="Химия", callback_data="Химия")
        btn6 = telebot.types.InlineKeyboardButton(text="Программирование", callback_data="Программирование")
        keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте,{res[0]} {res[1]}.\n"
                                                       f"Выберите свой предмет", reply_markup=keyboard)


def user_profile(message, res,selected_time = False):
    chat_id = message.chat.id
    if selected_time == True:
        res = function_bot.check(users[chat_id]["login"],users[chat_id]['password'])
    resu = []
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton(text="Расписание на неделю ", callback_data="week")
    btn2 = telebot.types.InlineKeyboardButton(text="Домашние задание", callback_data="home_work")
    btn3 = telebot.types.InlineKeyboardButton(text="Оценки", callback_data="evaluations")
    if  res[4] is None:
        resu = function_bot.predment_list(users[chat_id]["login"])
        btn4 = telebot.types.InlineKeyboardButton(text="Добавить расписание уроков", callback_data="week_new")
        keyboard.add(btn1, btn2, btn3, btn4)
    else:
        resu = function_bot.predment_list(users[chat_id]["login"])
        keyboard.add(btn1, btn2, btn3)
    if len(resu) == 2:
        subjetc = "\n".join(resu)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте, {res[2]} {res[1]}.\n"
                                                       f"Ваш предмет {subjetc}.\n"
                                                       f"Мы каждый месяц будем писать сколько у вас осталось срок обучения",
                         reply_markup=keyboard)
    else:
        subjetc = "\n".join(resu)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте, {res[2]} {res[1]}.\n"
                                                       f"Ваши предметы {subjetc}.\n"
                                                       f"Мы каждый месяц будем писать сколько у вас осталось срок обучения",
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['week', 'home_work', 'evaluations', 'week_new'])
def handler_main(call):
    chat_id = call.message.chat.id

    if chat_id not in users:
        users[chat_id] = {'index_photo': 0, 'teachers': []}

    student = function_bot.check(login=users[chat_id]['login'], password=users[chat_id]["password"], check_predmet=1)
    
    subjects = student[-2]
    users[chat_id]['subjects'] = subjects

    if call.data == "week_new":
        bot.send_message(chat_id,
                         "Привет, наш дорогой друг! \nСейчас тебе предстоит сделать самый сложный выбор — выбор предмета. Пожалуйста, выбери предмет, по которому ты хочешь увидеть учителей.")
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        for subject in subjects:
            button = telebot.types.InlineKeyboardButton(text=subject, callback_data=f"subject_{subject}")
            keyboard.add(button)

        bot.send_message(chat_id, "Выберите предмет:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('subject_'))
def handle_subject_choice(call):
    chat_id = call.message.chat.id
    subject = call.data.split('_')[1].replace('_', ' ')  

    student = function_bot.check(login=users[chat_id]['login'], password=users[chat_id]["password"], check_predmet=1)
    teachers = []
    for subj in student[-1]:
        if subj == subject: 
            teachers.extend(function_bot.teacher_list(subj))

    if teachers:
        bot.send_message(chat_id, f"Вот учителя по предмету {subject}:")
        send_photo_with_buttons(chat_id, teachers)
    else:
        bot.send_message(chat_id, f"Извините, учителей для предмета {subject} нет.")

def send_photo_with_buttons(chat_id, teachers):
    for teacher in teachers:
        photo_url = teacher.get('photo_url')
        name = teacher.get('name')
        subject = teacher.get('subject')

        keyboard = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text=f"Подробнее о {name}", callback_data=f"teacher_{name}")
        keyboard.add(button)

        bot.send_photo(chat_id, photo_url, caption=f"{name} - {subject}", reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data in ["prev", "next", "ok","main_menu"])
def handle_callback(call):
    chat_id = call.message.chat.id
    if call.data == "main_menu":
        user_profile(chat_id,res=[],selected_time=True)

    if chat_id not in users:
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начни заново.")
        return

    index_photo = users[chat_id]['index_photo']
    teachers_list = users[chat_id]['teachers']

    if call.data == 'prev':
        index_photo = (index_photo - 1) % len(teachers_list)
    elif call.data == 'next':
        index_photo = (index_photo + 1) % len(teachers_list)
    elif call.data == 'ok':
        selected_teacher = teachers_list[index_photo]
        bot.send_message(chat_id, f"Вы выбрали учителя: {selected_teacher.name} {selected_teacher.fullname}!\n Напишите время расписание")
        bot.register_next_step_handler(call.message,selected_time,selected_teacher.name,selected_teacher.fullname,selected_teacher.predment)
        return

    users[chat_id]['index_photo'] = index_photo
    send_photo_with_buttons(chat_id, teachers_list)





@bot.callback_query_handler(func=lambda call: call.data in ["restart", "password_restart"])
def handle_query(call):
    if call.data == "restart":
        bot.send_message(call.message.chat.id, "Заново!")
        hello_start(call.message)
    else:
        bot.send_message(call.message.chat.id, "Восстановить пароль")
        hello_start(call.message)


@bot.message_handler(content_types=["photo"])
def photo_teach(message):
    chat_id = message.chat.id
    text = function_bot.save_photo(message, users[chat_id]["login"], bot)
    bot.send_message(message.chat.id, text[0])
    teacher_profile(message, text[1:])


@bot.callback_query_handler(
    func=lambda call: call.data in ["Математика", "Физика", "Программирование", "Химия", "География", "Информаткиа"])
def save_predment_teacher(call):
    chat_id = call.message.chat.id
    r = call.data
    result2 = function_bot.save_teacher_predment(login=users[chat_id]["login"], predment=r)
    bot.send_message(call.message.chat.id, "Сохранено")
    teacher_profile(call.message, result2)

def notify_teacher(subject_name, student_login):
    try:
        teacher = User.objects.filter(predment__icontains=subject_name, profile="teacher").first()
        if teacher and teacher.chat_id:
            bot.send_message(
                teacher.chat_id,
                f"Ученик {student_login} выбрал ваш предмет: {subject_name}."
            )
    except Exception as e:
        print(f"Ошибка при уведомлении учителя: {e}")

#выбор времени
def selected_time(message,teacher_name,teacher_fullname,subject_teach):
    time = message.text
    chat_id = message.chat.id
    result_time = function_bot.result_time(time,teacher_fullname,users[chat_id]["login"],subject_name = subject_teach)
    bot.send_message(chat_id,"Отлично вы выбрали расписание: " + result_time + "\n"
                     "Вы будете заниматься у учителя: " + teacher_name +  " " +  teacher_fullname)
    user_profile(message,res = result,selected_time=True)
if __name__ == '__main__':
    print("ок")
    bot.polling(none_stop=True)