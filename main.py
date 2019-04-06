import mysql.connector
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import time
import datetime

import threading
from threading import Thread, Timer





API_TOKEN = '830214956:AAFydska5qxwRXBxXgF6TbwYrEYAokGBHfE'

bot = telebot.TeleBot(API_TOKEN)

REFCOUNT = 10

def printit():
  threading.Timer(3600.0, printit).start()
  print("Hello, World!")
  status = bot.get_chat_member("@nedocoder",	630184594)
  print(status)

#printit()

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def DBUpdater():
    checkUser()  # isActiveUser Status
    checkTask()  # Check Tasks


timer = RepeatTimer(3600, DBUpdater)
timer.start()


def checkTask():
    dateNow = datetime.datetime.now()
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    req = "SELECT \
      users.id AS user, \
      users.invitedCount as invCount, \
      actions.userId AS task, \
      actions.id as taskId, \
      actions.channelName as channel, \
      actions.actionDate as actiondDate, \
      actions.status as actiondStatus \
      FROM users \
      INNER JOIN actions ON users.id = actions.userId AND users.invitedCount > 9 AND actions.status = 'pending'"
    mycursor.execute(req)
    tasks = mycursor.fetchall()
    for task in tasks:
        print("TASK",task)
        isChannelMember = bot.get_chat_member(task[4], task[0]).status
        actionDate = datetime.datetime.strptime(task[5], '%Y-%m-%d')
        if isChannelMember == "member" and (dateNow - actionDate).days >= 4:
            print("Юзер подписан и прошло 4 дня")
            req_setComplete = "UPDATE actions SET status = 'complete' WHERE id = %s"
            val_setComplete  = (task[3],)
            mycursor.execute(req_setComplete, val_setComplete)
            req_updateBalance = "UPDATE users SET balance = balance + 100 WHERE id = %s"
            val_updateBalance = (task[0],)
            mycursor.execute(req_updateBalance, val_updateBalance)
            mydb.commit()





def checkUser():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    req = "SELECT * FROM users WHERE isActiveUser = 0 OR isActiveRef = 0"
    mycursor.execute(req)
    usersList = mycursor.fetchall()
    for user in usersList:
        print(user)
        if user[5] == 0:
            req_CheckTasks = "SELECT * FROM actions WHERE userId = %s AND status = 'complete'"
            val_CheckTasks = (user[0],)
            mycursor.execute(req_CheckTasks, val_CheckTasks)
            taskList = mycursor.fetchall()
            if len(taskList) >= 10:
                setActiveUser(user[0],user[3])
                print("User Is active", user[0])
            else:
                print("User is not active")



def setActiveUser(userId, parentId):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    sql_count = "UPDATE users SET isActiveUser = 1 WHERE id = %s"
    val_count = (userId,)
    mycursor.execute(sql_count, val_count)
    if parentId != None:
        print(parentId)
        req_updateRefCount = "UPDATE users SET invitedCount = invitedCount + 1 WHERE id = %s"
        val_updateRefCount = (parentId,)
        mycursor.execute(req_updateRefCount, val_updateRefCount)
    mydb.commit()
    print(mycursor.rowcount, "User active updated")


def updateUser(userId):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    print(userId)
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE invitedBy = %s"
    val = (userId,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
        if x[4] >= 10:
            sql_count = "UPDATE users SET invitedCount = invitedCount + 1 WHERE id = %s"
            val_count = (userId,)
            mycursor.execute(sql_count, val_count)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        else:
            print("User invited < 10")


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

def gen_markup_dynamic(url, channelId):
    dataChannel = 'cb_getReward,{0}'.format(channelId)
    dataSkip = 'cb_skip,{0}'.format(channelId)
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Вступить в группу", url=url,
                                    callback_data=f"cb_targetChannel"),
               InlineKeyboardButton("Получить награду", callback_data=dataChannel),
               InlineKeyboardButton("Пропустить задание", callback_data=dataSkip))
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

def updateActiveBalance(actionId):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    print("Update action",actionId)
    mycursor = mydb.cursor()
    sql = "UPDATE actions SET status = 'complete' WHERE id = %s"
    val = (actionId,)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record(s) affected")

def getBalance(user):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    req_pendingBalance = "SELECT * FROM actions WHERE userId = %s AND status = 'pending'"
    val = (user.id,)
    mycursor.execute(req_pendingBalance, val)
    myresult = mycursor.fetchall()

    finalWaitingBalance = 0;
    activeBalance = 0
    print(myresult)
    for x in myresult:
        print(myresult)
        finalWaitingBalance += x[4]
    reqActive = "SELECT balance FROM users WHERE id = %s"
    mycursor.execute(reqActive, val)
    myresult = mycursor.fetchall()
    activeBalance = myresult[0][0]
    print(finalWaitingBalance)
    bot.send_message(user.id, "Баланс в ожидании: {0} руб\nДоступно к выводу: {1} руб".format(finalWaitingBalance, activeBalance))



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
def getChannel(userId, userName, lastMsg = None, skipped = None):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    if skipped == None:
        mycursor.execute("SELECT * FROM channels WHERE currentAmount < finalAmount AND JSON_CONTAINS(`users`, JSON_OBJECT('user', %s)) = 0", (userId,))
    else:
        mycursor.execute("SELECT * FROM channels WHERE channelName != %s AND currentAmount < finalAmount AND JSON_CONTAINS(`users`, JSON_OBJECT('user', %s)) = 0", (userId, skipped))

    myresult = mycursor.fetchall()
    nowork = False
    print(myresult)
    i = 0
    for x in myresult:
        i += 1
        try:
            isChannelMember = bot.get_chat_member(x[1], userId)
            isChannelMember = str(isChannelMember.status)
            if isChannelMember == "left":
                print(x[2],x[1])
                # bot.edit_message_text('Edit test', chat_id=user, message_id=msgId)
                if lastMsg != None:
                    bot.edit_message_text('Подпишись на канал {0} и получи 100 руб на счет'.format(x[1]), chat_id=userId, message_id=lastMsg, reply_markup=gen_markup_dynamic(x[2], x[1]))
                else:
                    bot.send_message(userId, 'Подпишись на канал {0} и получи 100 руб на счет'.format(x[1]), reply_markup=gen_markup_dynamic(x[2], x[1]))
                print('user not sub')
                nowork = False
                break
            else:
                print('Not have any job')
                nowork = True
        except Exception as e:
            if i == len(myresult):
                nowork = True
            print(e)
            continue
    if nowork or len(myresult) == 0:
        bot.send_message(userId, "Прости, но задач временно нет!")


def checkCompleteSubscription(channelId, userId, lastMsg):
    isChannelMember = bot.get_chat_member(channelId, userId)
    print("Is Member", isChannelMember)
    if isChannelMember.status == "member":
        print('member')
        updateChannelCount(channelId, userId, lastMsg)
    else:
        print('Не подписан')


def updateChannelCount(channelId, userId, lastMsg):
    now = time.strftime('%Y-%m-%d')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    print(channelId)
    print("Update Channel Count")
    mycursor = mydb.cursor()
    sql = "UPDATE channels SET currentAmount = currentAmount+1, users=JSON_ARRAY_APPEND(users, '$', JSON_OBJECT('user', %s,'date', %s)) WHERE channelName = %s"
    #sql_bal = "UPDATE users SET balance = balance+100 WHERE  id = %s"
    sql_trans = "INSERT INTO actions(userId, channelName, actionDate, earned) VALUES (%s, %s, %s, %s)"
    #val_bal = (userId,)
    # sql = "UPDATE channels SET users=JSON_ARRAY_APPEND(users, '$', JSON_OBJECT('user', 'traemz','date', '2990-33-22')) WHERE channelName = '@nedocoder'"
    val = (userId, now, channelId)
    val_trans = (userId, channelId, now, 100)
    mycursor.execute(sql, val)
    #mycursor.execute(sql_bal, val_bal)
    mycursor.execute(sql_trans, val_trans)
    bot.edit_message_text('Ты заработал 100 рублей', chat_id=userId, message_id=lastMsg, reply_markup=gen_markup_next())
    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")


def getRefCount(data):
    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="moneybot",
            port="8889"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id FROM users WHERE id = %s", (data.id,))
    myresult = mycursor.fetchall()
    return len(myresult)

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
        getChannel(call.from_user.id, call.from_user.username, call.message.message_id)  # get channel for subscribe
    elif "cb_skip" in data:
        reward = data.split(',')
        print(reward)
        getChannel(call.from_user.id, call.from_user.username,call.message.message_id, reward[1])  # get channel for subscribe
    elif call.data == "cb_rules":
        bot.answer_callback_query(call.id, "Click Rules")
    elif call.data == "cb_inviteFriends":
        bot.answer_callback_query(call.id, "Click Invite")
        bot.send_message(call.from_user.id, 'Твоя уникальня ссылка: https://t.me/evanmoney_bot?start={}'.format(call.from_user.username))
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

@bot.message_handler(commands=['checkref'])
def check_activeRef(message):
    print("Check Active Ref")
    updateUser(message.chat.id)



@bot.message_handler(commands=['updatebal'])
def update_balance(message):
    dateNow = datetime.datetime.now()
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="moneybot",
        port="8889"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM actions WHERE userId = %s AND status = 'pending'"
    val = (message.chat.id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    finalBalance = 0;

    for x in myresult:
        print(x)
        actionDate = datetime.datetime.strptime(x[3], '%Y-%m-%d')
        print("Сколько прошло дней", (dateNow - actionDate).days)
        if((dateNow - actionDate).days >= 4):
            updateActiveBalance(x[0])
        else:
            finalBalance += x[4]
    print(finalBalance)
    bot.send_message(message.chat.id, "Баланс в ожидании: {0} руб\nДоступно к выводу: 0".format(finalBalance))



@bot.message_handler(commands=['test2'])
def send_welcome(message):
    DBUpdater()
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     passwd="root",
    #     database="moneybot",
    #     port="8889"
    # )
    # mycursor = mydb.cursor()
    #
    # mycursor.execute("SELECT * from `channels` WHERE JSON_CONTAINS(`users`, JSON_OBJECT('user', 'tr1emz'))")
    #
    # myresult = mycursor.fetchall()
    # print(myresult)
    # for x in myresult:
    #     print(x)


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    print(unique_code)
    print('Create user')
    createUser(message.chat)  # create user if not exist

    if unique_code != None:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="moneybot",
            port="8889"
        )
        mycursor = mydb.cursor()
        sql = "UPDATE users SET invitedBy = %s WHERE id = %s"
        #sql_count = "UPDATE users SET invitedCount = invitedCount + 1 WHERE id = %s"
        #val_count = (unique_code,)
        val = (unique_code, message.chat.id)
        mycursor.execute(sql, val)
        #mycursor.execute(sql_count, val_count)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")

    bot.send_message(message.chat.id,
                     '{0}, вижу ты хочешь подзаработать? Твой id: {1}'.format(message.chat.username, message.chat.id),
                     reply_markup=gen_markup_starter())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == 'Заработать':
        getChannel(message.from_user.id, message.chat.username)  # get channel for subscribe
    elif message.text == 'Баланс':
        #bot.send_message(message.chat.id, '{0}, твой баланс 0 руб'.format(message.chat.username))
        getBalance(message.chat)
    elif message.text == 'Правила':
        bot.send_message(message.chat.id,
                         '❗{0}, с помощью этого бота можно хорошо заработать! Выполняйте задания и зарабатывайте деньги!'.format(
                             message.chat.username))
    elif message.text == 'Пригласить друзей':
        bot.send_message(message.chat.id, 'Ддя вывода средств требуется пригласить 5 друзей.\nТвоя уникальня ссылка: \nhttps://t.me/evanmoney_bot?start={}'.format(message.chat.id), disable_web_page_preview=None)
    elif message.text == 'Вывод':
        refCount = getRefCount(message.chat)
        if refCount >= REFCOUNT:
            bot.send_message(message.chat.id, '{0}, добавь свой киви кошелек'.format(message.chat.username))
        else:
            bot.send_message(message.chat.id, 'Для вывода нужно 5 рефералов\nУ вас:{0}'.format(refCount))



bot.polling(none_stop=True)
