import os
import django
import confing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store.settings')

django.setup()
from Users.models import User
import telebot
import function_bot_rez

bot = telebot.TeleBot(confing.token_bot)
users={}
chat_id_user = 0
chat_id_admin = 0
predment_global = ""
name_global = ""
fullname_global = ""

@bot.message_handler(commands=['start'])
def hello_start(message):
    chat_id = message.chat.id
    users[chat_id] = {}
    bot.send_message(chat_id, "Привет! Меня зовут Бал.\n Я помогу тебе решить некоторые вопросы. Введи свой логин:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_login)

def save_login(message):
    chat_id = message.chat.id
    users[chat_id]["login"] = message.text
    bot.send_message(chat_id,f"Отлично,{message.text} !Теперь введи свой пароль.")
    bot.register_next_step_handler(message,save_password)

def save_password(message):
    chat_id = message.chat.id
    users[chat_id]["password"] = message.text
    result = function_bot_rez.check_username(login = users[chat_id]["login"],password = users[chat_id]["password"],chat_id_user=chat_id)
    if result[0] == 3:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton(text="Заново",callback_data="restart")
        btn2 = telebot.types.InlineKeyboardButton(text="Забыли пароль",callback_data="restart")
        markup.add(btn1,btn2)
        bot.send_message(chat_id,"Неверный логин или пароль",reply_markup=markup)
    elif result[0] == 2:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(text="Вернутся на сайт")
        bot.send_message(chat_id,"Вернитесь на сайт и выбирите предмет.",reply_markup=markup)
    elif result[0] == 1 and result[2] == None:
        name_global = result[3]
        fullname_global = result[-2]
        predment_global = result[1].replace(" ", ",")
        user_profile(message,predment_global,name_global,fullname_global)
    else:
            name_global = result[3]
            fullname_global = result[-2]
            predment_global = result[1].replace(" ", ",")
            chat_id_admin = result[-1]
            admin_profile(message,name_global,fullname_global)

def user_profile(message,predmet,name,fullname):
    bot.send_message(message.chat.id,f"Здраствуйте , {name} {fullname}\nВаши предметы:{predmet[:-1]}\nНапишите ваш вопрос.")
    bot.register_next_step_handler(message,send_message_admin)


def send_message_admin(message):
    bot.send_message(chat_id=chat_id_admin,text=f"Вам пришел вопрос.{message.text}")
    if chat_id_admin != 0:
        bot.register_next_step_handler(message,send_message_user)


def send_message_user(message):
    bot.send_message(chat_id=chat_id_user,text=f"Вам пришел ответ на ваш вопрос.{message.text}")
    user_profile(message,predment_global,name_global,fullname_global)

def admin_profile(message,name,fullname):
    bot.send_message(chat_id=message.chat.id,text=f"Здраствуйте,{fullname} {name}")
@bot.callback_query_handler(func=lambda call:call.data in ["restart"])
def handler_callback(call):
    if call.data == "restart":
        bot.send_message(call.message.chat.id,"Заново!")
        hello_start(call.message)

if __name__ == "__main__":
    print("ОК")
    bot.polling(non_stop=True)
