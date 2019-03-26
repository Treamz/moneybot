
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

TELEGRAM_TOKEN = '830214956:AAFydska5qxwRXBxXgF6TbwYrEYAokGBHfE'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def gen_markup():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data=f"cb_yes"),
    InlineKeyboardButton("No", callback_data=f"cb_no"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call)
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.send_message(message.chat.id, "Yes/no?", reply_markup=gen_markup())

bot.polling(none_stop=True)