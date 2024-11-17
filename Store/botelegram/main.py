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
index_photo = 0
check_index_techer = False

@bot.message_handler(commands=['start'])
def hello_start(message):
    chat_id = message.chat.id
    users[chat_id] = {} 
    bot.send_message(chat_id, "Привет! Введи свой логин:",reply_markup=telebot.types.ReplyKeyboardRemove())
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
    if result[0] == 2:

        if result[5] == "teacher":
            if result[6]  is None:
                bot.send_message(message.chat.id, "Отправьте ваше фото")
            elif result[6]  is not None:
                teacher_profile(message=message, res=result)
        else:
            user_profile(message=message, res=result)

    if result[0] == 3:
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_teacher = telebot.types.InlineKeyboardButton(text="Заново", callback_data="restart")
        keyboard.add(button_teacher)
        bot.send_message(chat_id, "Неправильный логин или пароль.",reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['teacher', 'student'])
def profile_selection(call):
    result = []
    dataprof = ""
    if call.data == 'teacher':
        bot.send_message(call.message.chat.id, "Вы выбрали: Учитель")
        dataprof = "teacher"
    elif call.data == 'student':
        bot.send_message(call.message.chat.id, "Вы выбрали: Ученик")
        dataprof = "student"
    user_login = users[call.message.chat.id]['login']
    function_bot.student_teacher(user_login,prof=dataprof)
    result = function_bot.check(login=users[call.message.chat.id]['login'],password= " ")
    if dataprof == "student":
        user_profile(message=call.message,res=result)
    if dataprof == "teacher" and result[6] is not None :
        teacher_profile(message=call.message,res=result)
    elif dataprof == "teacher" and result[6] is None:
        bot.send_message(call.message.chat.id, "Отправьте ваше фото")

def teacher_profile(message,res):
    chat_id = message.chat.id
    if type(res[0]) == int and res[len(res)-1] is not None:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Расписание на неделю ", callback_data="week")
        btn2 = telebot.types.InlineKeyboardButton(text="Домашние задание", callback_data="home_work")
        btn3 = telebot.types.InlineKeyboardButton(text="Оценки", callback_data="evaluations")
        keyboard.add(btn1, btn2, btn3)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте, {res[1]} {res[2]}.\n", reply_markup=keyboard)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Георафия",callback_data="Георафия")
        btn2 = telebot.types.InlineKeyboardButton(text="Физика",callback_data="Физика")
        btn3 = telebot.types.InlineKeyboardButton(text="Математика",callback_data="Математика")
        btn4 = telebot.types.InlineKeyboardButton(text="Информатика",callback_data="Информатика")
        btn5 = telebot.types.InlineKeyboardButton(text="Химия",callback_data="Химия")
        btn6 = telebot.types.InlineKeyboardButton(text="Программирование",callback_data="Программирование")
        keyboard.add(btn1, btn2, btn3,btn4, btn5, btn6)
        bot.send_message(chat_id=message.chat.id, text=f"Здраствуйте,{res[0]} {res[1]}.\n"
                                                       f"Выберите свой предмет", reply_markup=keyboard)

def user_profile(message,res):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton(text = "Расписание на неделю ",callback_data = "week")
    btn2 = telebot.types.InlineKeyboardButton(text="Домашние задание", callback_data = "home_work")
    btn3 = telebot.types.InlineKeyboardButton(text="Оценки",callback_data = "evaluations")
    if res[4] is None:
        btn4 = telebot.types.InlineKeyboardButton(text="Добавить расписание уроков",callback_data = "week_new")
        keyboard.add(btn1, btn2, btn3, btn4)
    else:
        keyboard.add(btn1,btn2,btn3)
        resu = function_bot.predment_list(users[chat_id]["login"])
    if len(res) == 1:
             bot.send_message(chat_id = message.chat.id, text=f"Здраствуйте, { res[2]} {res[1]}.\n "
                                                              f"Ваш предмет {str(res[0])}.\n"
                                                              f"Мы каждый месяц будем писать сколько у вас осталось срок обучения",reply_markup=keyboard)
    else:
        subjetc = "\n".join(result)
        bot.send_message(chat_id=message.chat.id,text=f"Здраствуйте, { res[2]} {res[1]}.\n"
                                                      f"Ваши предметы {subjetc}.\n"
                                                              f"Мы каждый месяц будем писать сколько у вас осталось срок обучения",reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['week', 'home_work','evaluations','week_new'])
def handler_main(call):
    chat_id = call.message.chat.id
    student = function_bot.check(login=users[chat_id]['login'], password=users[chat_id]["password"])
    techears = function_bot.teacher_list(student[-1])



    match (call.data):
        case "week_new":
            bot.send_message(chat_id,
                             "Привет, наш дорогой друг! \nСейчас тебе предстоит сделать самый сложный выбор — выбор расписания. Сейчас перед тобой появится список учителей, их фото и регалии.")
            send_photo_with_buttons(chat_id, techears,False)


def send_photo_with_buttons(chat_id, teacher,check_index_techer):

    global index_photo
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    if index_photo > 0:
        keyboard.add(
            telebot.types.InlineKeyboardButton("Влево", callback_data='prev')
        )

    keyboard.add(
        telebot.types.InlineKeyboardButton("Вправо", callback_data='next'),
        telebot.types.InlineKeyboardButton("ОК", callback_data='ok')
    )
    if check_index_techer == False:
        check_index_techer = True
        teacher_photo = teacher[index_photo].photo_teacher
    else:
        teacher_photo = teacher.photo_teacher

    if os.path.isfile(teacher_photo):
        with open(teacher_photo, "rb") as photo:
            bot.send_photo(chat_id, photo, reply_markup=keyboard)
    else:
        bot.send_photo(chat_id, teacher_photo, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["prev", "next", "ok"])
def handle_callback(call):
    global index_photo
    chat_id = call.message.chat.id

    student = function_bot.check(login=users[chat_id]['login'], password=users[chat_id]["password"])
    techear = function_bot.teacher_list(student[-1])


    if call.data == 'prev':
        index_photo = (index_photo - 1) % len(techear)
    elif call.data == 'next':
        index_photo = (index_photo + 1) % len(techear)
    elif call.data == 'ok':
        bot.send_message(chat_id, "Вы выбрали учителя.")

    send_photo_with_buttons(chat_id, techear[index_photo],True)
@bot.callback_query_handler(func=lambda call: call.data == "restart")
def handle_query(call):
    bot.send_message(call.message.chat.id, "Заново!")
    hello_start(call.message)

@bot.message_handler(content_types=["photo"])
def photo_teach(message):
    chat_id = message.chat.id
    text = function_bot.save_photo(message,users[chat_id]["login"],bot)
    bot.send_message(message.chat.id,text[0])
    teacher_profile(message,text[1:])

@bot.callback_query_handler(func=lambda call: call.data in ["Математика","Физика","Программирование","Химия","География","Информаткиа"])
def save_predment_teacher(call):
    chat_id = call.message.chat.id
    r = call.data
    result = function_bot.save_teacher_predment(login = users[chat_id]["login"],predment=r)
    bot.send_message(call.message.chat.id,"Сохранено")
    teacher_profile(call.message,result)





if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()
