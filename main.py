import mysql.connector
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import time

API_TOKEN = '830214956:AAFydska5qxwRXBxXgF6TbwYrEYAokGBHfE'

bot = telebot.TeleBot(API_TOKEN)

def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

def gen_markup_dynamic(url, channelId):
    dataChannel = 'cb_getReward,{0}'.format(channelId)
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Вступить в группу", url=url,
                                    callback_data=f"cb_targetChannel"),
               InlineKeyboardButton("Получить награду", callback_data=dataChannel),
               InlineKeyboardButton("Пропустить задание", callback_data=f"cb_skip"))
    return markup

def gen_markup_next():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Назад", callback_data=f"cb_getNewAction"))
    return markup


def gen_markup_starter():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Заработать"),
               InlineKeyboardButton("Баланс"),
               InlineKeyboardButton("Правила"),
               InlineKeyboardButton("Пригласить друзей"),
               InlineKeyboardButton("Вывод"))
    return markup


def createUser(data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO users (id, username, balance) VALUES (%s, %s, %s)"
    val = (data.id, data.username, '0')
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")

# Get Channel
def getChannel(userId, userName):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT channelName, channelLink FROM channels")

    myresult = mycursor.fetchall()
    nowork = False
    for x in myresult:
        try:
            isChannelMember = bot.get_chat_member(x[0], userId)
            isChannelMember = str(isChannelMember.status)
            if isChannelMember == "left":
                #bot.edit_message_text('Edit test', chat_id=user, message_id=msgId)
                bot.send_message(userId, 'Подпишись на канал {0} и получи 100 руб на счет'.format(x[0]), reply_markup=gen_markup_dynamic(x[1], x[0]))
                print('user not sub')
                nowork = False
                break
            else:
                print('Not have any job')
                nowork = True
        except Exception as e:
            print(e)
            continue
    if nowork:
        bot.send_message(userId, "Прости, но задач временно нет!")

def checkCompleteSubscription(channelId, userId, lastMsg):
    isChannelMember = bot.get_chat_member(channelId, userId)
    if isChannelMember:
        print('member')
        updateChannelCount(channelId, userId, lastMsg)
    else:
        print('Не подписан')


def updateChannelCount(channelId, userId, lastMsg):
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    print(channelId)
    mycursor = mydb.cursor()
    sql = "UPDATE channels SET currentAmount = currentAmount+1, users=JSON_ARRAY_APPEND(users, '$', JSON_OBJECT('user', %s,'date', %s)) WHERE channelName = %s"
    #sql = "UPDATE channels SET users=JSON_ARRAY_APPEND(users, '$', JSON_OBJECT('user', 'traemz','date', '2990-33-22')) WHERE channelName = '@nedocoder'"
    val = (userId, now, channelId)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record(s) affected")
    bot.edit_message_text('Ты заработал 100 рублей', chat_id=userId, message_id=lastMsg, reply_markup=gen_markup_next())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    if 'cb_getReward' in data:
        reward = data.split(',')
        print(reward[1], call.from_user.id, call.message.message_id)
        checkCompleteSubscription(reward[1], call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Get Reward")
    # if call.data == "cb_getReward":
    #     bot.answer_callback_query(call.id, "Get Reward")
    #     #checkCompleteSubscription()
    #     bot.edit_message_text('Edit test', chat_id=call.from_user.id, message_id=call.message.message_id, )
    elif call.data == "cb_balance":
        bot.answer_callback_query(call.id, "Click Balance")
        bot.send_message(call.from_user.id, '{0}, твой баланс: 0 руб.'.format(call.from_user.username))
        print(call.from_user.id)
    elif call.data == "cb_getNewAction":
        getChannel(call.from_user.id, call.from_user.username)  # get channel for subscribe
    elif call.data == "cb_rules":
        bot.answer_callback_query(call.id, "Click Rules")
    elif call.data == "cb_inviteFriends":
        bot.answer_callback_query(call.id, "Click Invite")
    elif call.data == "cb_withdraw":
        bot.answer_callback_query(call.id, "Click withdraw")


# Handle '/start' and '/help'
@bot.message_handler(commands=['test'])
def send_welcome(message):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    sql = "UPDATE channels SET users=JSON_ARRAY_APPEND(users, '$', JSON_OBJECT('user', 'traemz','date', '2990-33-22')) WHERE channelName = '@nedocoder'"
    mycursor.execute(sql,)
    mydb.commit()
    print(mycursor.rowcount, "record(s) affected")


@bot.message_handler(commands=['test2'])
def send_welcome(message):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * from `channels` WHERE JSON_CONTAINS(`users`, JSON_OBJECT('user', 'tr1emz'))")

    myresult = mycursor.fetchall()
    print(myresult)
    for x in myresult:
        print(x)


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    print(unique_code)
    bot.send_message(message.chat.id,
                     '{0}, вижу ты хочешь подзаработать? Твой id: {1}'.format(message.chat.username, message.chat.id),
                     reply_markup=gen_markup_starter())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == 'Заработать':
        print('Create user')
        createUser(message.chat)  # create user if not exist
        getChannel(message.from_user.id, message.chat.username)  # get channel for subscribe
    elif message.text == 'Баланс':
        bot.send_message(message.chat.id, '{0}, твой баланс 0 руб'.format(message.chat.username))
    elif message.text == 'Правила':
        bot.send_message(message.chat.id,
                         '❗{0}, с помощью этого бота можно хорошо заработать! Выполняйте задания и зарабатывайте деньги!'.format(
                             message.chat.username))
    elif message.text == 'Пригласить друзей':
        bot.send_message(message.chat.id, '{0}, ты пригоаси 0 друзей'.format(message.chat.username))
    elif message.text == 'Вывод':
        bot.send_message(message.chat.id, '{0}, добавь свой киви кошелек'.format(message.chat.username))


bot.polling(none_stop=True)
