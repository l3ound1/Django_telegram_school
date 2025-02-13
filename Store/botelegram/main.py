import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')

import django
django.setup()
import confing
import telebot
import function_bot
import schedule 
import time
from datetime import datetime, timedelta
import threading
from collections import defaultdict
import google_meet
predmet = ""
day = ""
bot = telebot.TeleBot(confing.token_bot)
users = {}
chat_id_user = None
chat_id_admin = None
meet_link = ""
lesson_links = {}

def get_day_of_week():
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    current_day = datetime.now().weekday()
    return days[current_day]
def send_lesson_to_student(student_chat_id, teacher_name, lesson_time, meet_link):
    bot.send_message(student_chat_id, f"У вас занятие с учителем {teacher_name} по предмету {lesson_time}.\nСсылка на урок: {meet_link}")

@bot.message_handler(commands=['start'])
def hello_start(message):
    chat_id = message.chat.id
    users[chat_id] = {}
    bot.send_message(chat_id, "Привет! Меня зовут Бал.\nЯ помогу тебе решить некоторые вопросы. Введи свой логин:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_login)

def send_lesson_reminder(chat_id, meet_link, lesson_datetime):
    time_to_wait_start = (lesson_datetime - datetime.now()).total_seconds()
    if time_to_wait_start > 0:
        time.sleep(time_to_wait_start)

    bot.send_message(chat_id, f"Пора начинать занятие! Ссылка {meet_link}")

def save_login(message):
    chat_id = message.chat.id
    users[chat_id] = {
        "login": message.text,
        "chat_id": chat_id,
        "status": "",
        "predment": "",
        "name":"",
        "fullnam":"",
        "profile":"",
    }
    bot.send_message(chat_id, f"Отлично, {message.text}! Теперь введи свой пароль.")
    bot.register_next_step_handler(message, save_password)

def save_password(message):
    global chat_id_user, chat_id_admin
    chat_id = message.chat.id
    users[chat_id]["password"] = message.text
    result = function_bot.check_username(login=users[chat_id]["login"], password=users[chat_id]["password"], chat_id_user=chat_id)
    
    if result[0] == 3:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Заново", callback_data="restart")
        btn2 = telebot.types.InlineKeyboardButton(text="Забыли пароль", callback_data="restart")
        markup.add(btn1, btn2)
        bot.send_message(chat_id, "Неверный логин или пароль", reply_markup=markup)
    elif result[0] == 2:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(text="Вернуться на сайт")
        bot.send_message(chat_id, "Вернитесь на сайт и выберите предмет.", reply_markup=markup)
    elif result[0] == 1 and result[2] is None:
        users[chat_id]["name"] = result[3]
        users[chat_id]["fullname"] = result[-3]
        users[chat_id]["predment"] = result[1].replace(" ", ",")
        chat_id_user = chat_id
        users[chat_id]["profile"] = True
        users[chat_id]["status"] = result[-1]
        user_profile(message)
    else:
        users[chat_id]["name"] = result[3]
        users[chat_id]["fullname"] = result[-2]
        users[chat_id]["predment"] = result[1].replace(" ", ",")
        chat_id_admin = result[-2]
        chat_id_user = chat_id
        admin_profile(message)

def user_profile(message):
    bot.send_message(message.chat.id, f"Здравствуйте, {users[message.chat.id]['name']} {users[message.chat.id]['fullname']}\nВаши предметы: {users[message.chat.id]['predment']}\nНапишите ваш вопрос.")
    bot.register_next_step_handler(message, send_message_admin)


def admin_profile(message):
    bot.send_message(chat_id=message.chat.id, text=f"Здравствуйте, {users[message.chat.id]['fullname']} {users[message.chat.id]['name']}. Вы вошли как администратор.")



def send_message_admin(message):
    if message.text == '/start':
        hello_start(message)
    global chat_id_admin

    if chat_id_admin is not None:
        bot.send_message(chat_id=chat_id_admin, text=f"Вам пришел вопрос от пользователя: {message.text}")
        bot.register_next_step_handler(message, wait_for_admin_response)
    else:
        bot.send_message(message.chat.id, "Администратор пока недоступен.")



def wait_for_admin_response(message):
    bot.send_message(chat_id=message.chat.id, text="Ожидайте ответа от администратора.")



@bot.message_handler(func=lambda message: message.chat.id == chat_id_admin)
def send_message_user(message):
    global chat_id_user

    if chat_id_user is not None:
        bot.send_message(chat_id=chat_id_user, text=f"Вам пришел ответ от администратора: {message.text}")
    else:
        bot.send_message(chat_id_admin, "Пользователь недоступен для ответа.")



def check_lesson_teacher(chat_id):
    global lesson_links
    day = get_day_of_week()
    now = datetime.now()

    teacher_res = function_bot.check_teacher_schedule_with_students(users[chat_id]["login"], day)

    if not teacher_res:
        bot.send_message(chat_id, "У вас сегодня нет занятий.")
        return

    schedule_dict = defaultdict(list)

    for start_time, lesson_time, student in teacher_res:
        schedule_dict[(start_time, lesson_time)].append(student)
        bot.send_message(chat_id, f"У вас сегодня занятие:\nУченик: {student.fullname if student.fullname else student.username}, Время: {lesson_time}")

    for (start_time, lesson_time), students in schedule_dict.items():
        lesson_datetime = datetime.combine(now.date(), datetime.strptime(lesson_time, "%H:%M").time())
        students_names = ", ".join([student.fullname if student.fullname else student.username for student in students])

        bot.send_message(chat_id, f"Напоминание: У вас сегодня занятие с учениками: {students_names} в {lesson_time}.\nМы вам скинем ссылку на урок. Время по МСК")

        email_teacher = function_bot.get_email(users[chat_id]["login"])

        if (users[chat_id]["login"], lesson_time) not in lesson_links:
            meet_link = google_meet.create_google_meet_event(email_teacher, lesson_time, 125)
            lesson_links[(users[chat_id]["login"], lesson_time)] = meet_link
        else:
            meet_link = lesson_links[(users[chat_id]["login"], lesson_time)]

        threading.Thread(target=send_lesson_reminder, args=(chat_id, meet_link, lesson_datetime)).start()

        for student in students:
            student_chat_id = student.id_t

            threading.Thread(target=send_lesson_to_student,args=(student_chat_id, users[chat_id]['name'], lesson_time, meet_link)).start()


def check_lesson_student(chat_id):
    global lesson_links
    day = get_day_of_week()
    now = datetime.now()
    predm_res = function_bot.check_predment(users[chat_id]["login"], day)

    if predm_res is None:
        bot.send_message(chat_id, "У вас сегодня нету занятия")
    else:
        lesson_time = datetime.strptime(predm_res[0], "%H:%M").time()
        lesson_datetime = datetime.combine(now.date(), lesson_time)

        bot.send_message(chat_id, f"У вас сегодня занятие по {predm_res[-1]} в {predm_res[0]}.\nМы скинем вам ссылку на урок.")

        teacher_login = predm_res[-1]
        if (teacher_login, predm_res[0]) in lesson_links:
            meet_link = lesson_links[(teacher_login, predm_res[0])]

            threading.Thread(target=send_lesson_reminder, args=(chat_id, meet_link, lesson_datetime)).start()
        else:
            bot.send_message(chat_id, "Ссылка на урок пока недоступна.")
def day_check():
    global lesson_links
    lesson_links.clear()
    for chat_id in users:
        if users[chat_id]["status"] == "teacher":
            check_lesson_teacher(chat_id)
        else:
            check_lesson_student(chat_id)



schedule.every().day.at("13:33").do(day_check)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    print("Бот запущен")
    threading.Thread(target=run_schedule).start()
    bot.polling(non_stop=True)