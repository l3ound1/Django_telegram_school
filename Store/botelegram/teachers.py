import telebot

from botelegram import function_bot
from botelegram.main import bot
from function_bot import teacher_list
import os

index_photo = 0


def send_photo_with_buttons(chat_id, teachers, check_index_teacher):
    global index_photo
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    if index_photo > 0:
        keyboard.add(telebot.types.InlineKeyboardButton("⬅️", callback_data='prev'))
    keyboard.add(
        telebot.types.InlineKeyboardButton("➡️", callback_data='next'),
        telebot.types.InlineKeyboardButton("Выбрать", callback_data='ok')
    )

    if check_index_teacher == False:
        teacher_photo = teachers[index_photo].photo_teacher
    else:
        teacher_photo = teachers[index_photo].photo_teacher

    if os.path.isfile(teacher_photo):
        with open(teacher_photo, "rb") as photo:
            bot.send_photo(chat_id, photo, reply_markup=keyboard)
    else:
        bot.send_photo(chat_id, teacher_photo, reply_markup=keyboard)


def handle_teacher_list(call):
    chat_id = call.message.chat.id
    r = call.data
    result = function_bot.save_teacher_predment(login=users[chat_id]["login"], predment=r)
    bot.send_message(call.message.chat.id, "Сохранено")
    handle_teacher_profile(call.message, result)


def handle_teacher_profile(message, res):
    chat_id = message.chat.id
    teachers = [teacher for subject in res[-1] for teacher in teacher_list(subject)]

    if not teachers:
        bot.send_message(chat_id, "Нет учителей для выбранного предмета.")
        return

    send_photo_with_buttons(chat_id, teachers, False)

