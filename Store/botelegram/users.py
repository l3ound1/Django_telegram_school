import os

import telebot
from botelegram.main import bot
import function_bot
from teachers import handle_teacher_profile

users = {}
index_photo = {}


# Функция, которая обрабатывает сообщения
def handle_message(message):
    chat_id = message.chat.id

    # Если пользователь еще не зарегистрирован, начинаем с логина
    if chat_id not in users:
        users[chat_id] = {'step': 1}  # Устанавливаем начальный шаг
        bot.send_message(chat_id, "Привет! Введи свой логин:")

    elif users[chat_id]['step'] == 1:  # Логин
        login = message.text
        users[chat_id]['login'] = login
        users[chat_id]['step'] = 2  # Переходим ко второму шагу
        bot.send_message(chat_id, f"Отлично, {login}. Теперь введи свой пароль:")

    elif users[chat_id]['step'] == 2:  # Пароль
        password = message.text
        users[chat_id]['password'] = password
        result = function_bot.check(login=users[chat_id]['login'], password=password)

        if result[0] == 1:
            keyboard = telebot.types.InlineKeyboardMarkup()
            button_teacher = telebot.types.InlineKeyboardButton(text="👩🏻‍🏫 Учитель", callback_data="teacher")
            button_student = telebot.types.InlineKeyboardButton(text="👨🏻‍🎓 Ученик", callback_data="student")
            keyboard.add(button_student, button_teacher)
            bot.send_message(chat_id, f"Здравствуй, {result[1]} {result[2]}\nВыбери свой профиль",
                             reply_markup=keyboard)
        elif result[0] == 2:
            handle_student_or_teacher(result, message)
        elif result[0] == 3:
            handle_invalid_login_or_password(message)


def handle_student_or_teacher(result, message):
    chat_id = message.chat.id
    if result[5] == "teacher":
        if result[6] is None:
            bot.send_message(chat_id, "Отправьте ваше фото.")
        else:
            handle_teacher_profile(message, result)
    else:
        user_profile(message, result)


def handle_invalid_login_or_password(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_teacher = telebot.types.InlineKeyboardButton(text="Заново", callback_data="restart")
    button_restart_password = telebot.types.InlineKeyboardButton(text="Восстановить пароль",
                                                                 callback_data="password_restart",
                                                                 url="http://127.0.0.1:8000/")
    keyboard.add(button_teacher, button_restart_password)
    bot.send_message(chat_id, "Неправильный логин или пароль.", reply_markup=keyboard)






def user_profile(message, res):
    resu = []
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton(text="Расписание на неделю", callback_data="week")
    btn2 = telebot.types.InlineKeyboardButton(text="Домашние задание", callback_data="home_work")
    btn3 = telebot.types.InlineKeyboardButton(text="Оценки", callback_data="evaluations")

    if res[4] is None:
        resu = function_bot.predment_list(users[chat_id]["login"])
        btn4 = telebot.types.InlineKeyboardButton(text="Добавить расписание уроков", callback_data="week_new")
        keyboard.add(btn1, btn2, btn3, btn4)
    else:
        resu = function_bot.predment_list(users[chat_id]["login"])
        keyboard.add(btn1, btn2, btn3)

    subject_list = "\n".join(resu)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуй, {res[2]} {res[1]}.\nВаши предметы: {subject_list}.\nМы каждый месяц будем писать, сколько у вас осталось срок обучения.",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data in ['week', 'home_work', 'evaluations', 'week_new'])
def handler_main(call):
    teachers = []
    chat_id = call.message.chat.id
    student = function_bot.check(login=users[chat_id]['login'], password=users[chat_id]["password"], check_predmet=1)
    teachers.append([teacher for subject in student[-1] for teacher in function_bot.teacher_list(subject)])

    if call.data == "week_new":
        bot.send_message(
            chat_id,
            "Привет, наш дорогой друг! \nСейчас тебе предстоит сделать самый сложный выбор — выбор расписания. Сейчас перед тобой появится список учителей, их фото и регалии."
        )
        send_photo_with_buttons(chat_id, teachers, False)


def send_photo_with_buttons(chat_id, teachers, check_index_teacher):
    global index_photo
    if chat_id not in index_photo:
        index_photo[chat_id] = 0  # Инициализируем индекс для каждого чата

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

    if index_photo[chat_id] > 0:
        keyboard.add(telebot.types.InlineKeyboardButton("⬅️", callback_data='prev'))

    keyboard.add(
        telebot.types.InlineKeyboardButton("➡️", callback_data='next'),
        telebot.types.InlineKeyboardButton("Выбрать", callback_data='ok')
    )

    teacher_photo = teachers[index_photo[chat_id]].photo_teacher

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
    teachers = function_bot.teacher_list(student[-1])

    if call.data == 'prev':
        index_photo[chat_id] = (index_photo[chat_id] - 1) % len(teachers)
    elif call.data == 'next':
        index_photo[chat_id] = (index_photo[chat_id] + 1) % len(teachers)
    elif call.data == 'ok':
        bot.send_message(chat_id, "Вы выбрали учителя.")

    send_photo_with_buttons(chat_id, teachers, True)


def handle_teacher_profile(message, res):
    chat_id = message.chat.id
    teachers = [teacher for subject in res[-1] for teacher in function_bot.teacher_list(subject)]

    if not teachers:
        bot.send_message(chat_id, "Нет учителей для выбранного предмета.")
        return

    send_photo_with_buttons(chat_id, teachers, False)
