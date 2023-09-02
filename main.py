import telebot
import sqlite3
import time

from telebot import types


bot = telebot.TeleBot()


waiting_for_title = False
waiting_for_text = False
waiting_for_antwort = False
waiting_for_antwort1 = False
waiting_for_antwort2 = False
waiting_for_plan = False
waiting_for_plan_text1 = False
waiting_for_plan_text2 = False
current_note_title = ""
current_note_antwort = ""
current_note_antwort2 = ""
current_note_antwort1 = ""
current_plan = ""
current_day = ""
def create_table():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        text TEXT
    )''')

    connect.commit()
    connect.close()

def create_table_todolist():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS todoist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        day_id TEXT,
        plan TEXT,
        number INTEGER
    )''')

    connect.commit()
    connect.close()


def add_note(user_id, title, text):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("INSERT INTO notes (user_id, title, text) VALUES (?, ?, ?)", (user_id, title, text))

    connect.commit()
    connect.close()

def get_user_notes(user_id):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("SELECT title FROM notes WHERE user_id = ?", (user_id,))
    notes = cursor.fetchall()

    connect.close()

    return [note[0] for note in notes]

def get_note_by_id(user_id, note_id):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("SELECT title, text FROM notes WHERE user_id = ? AND title = ?", (user_id, note_id))
    note = cursor.fetchone()

    connect.close()

    return note
def open_note_id_handler(user_id, note_id):
    note = get_note_by_id(user_id, note_id)

    if note:
        note_title = note[0]
        note_text = note[1]
        reply = f"заметка : {note_title}\n\n{note_text}"
    else:
        reply = "похоже, такой заметки пока нет.."

    bot.send_message(user_id, reply)


def delete_note_by_id(user_id, note_id):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM notes WHERE user_id = ? AND title = ?", (user_id, note_id))
    connect.commit()  # Применить изменения в базе данных
    connect.close()


def delete_note_id_handler(user_id, note_id):
    delete_note_by_id(user_id, note_id)

    if note_id:
        reply = "готово"
    else:
        reply = "похоже, такой заметки и так нет.."

    bot.send_message(user_id, reply)


def add_plan(user_id, day_id, plan):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("SELECT COUNT(*) FROM todoist WHERE user_id = ? AND day_id = ?", (user_id, day_id))
    num_tasks = cursor.fetchone()[0] + 1  # текущее число задач плюс один
    cursor.execute("INSERT INTO todoist (user_id, day_id, plan, number) VALUES (?, ?, ?, ?)",
                   (user_id, day_id, plan, num_tasks))
    connect.commit()
    connect.close()

def get_plan_by_id(user_id, day_id):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    # Извлекаем все строки с заданным day_id
    cursor.execute("SELECT plan FROM todoist WHERE user_id = ? AND day_id = ?", (user_id, day_id))
    rows = cursor.fetchall()

    connect.close()

    # Если есть хотя бы одна строка с заданным day_id, возвращаем список планов с порядковыми номерами
    if rows:
        return [f"{i+1}. {row[0]}" for i, row in enumerate(rows)]
    else:
        return []
def open_plan_id_handler(user_id, day_id):
    plans = get_plan_by_id(user_id, day_id)

    if plans:
        reply = f"{day_id} :\n\n" + "\n".join(plans)
    else:
        reply = f"{day_id} :\n" + "\nпланов нет, юху!"

    bot.send_message(user_id, reply)


def delete_plan_by_id(user_id, day_id, number):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM todoist WHERE user_id = ? AND day_id = ? AND number = ?", (user_id, day_id, number))
    connect.commit()
    connect.close()


def delete_plan_id_handler(user_id, day_id, number):
    delete_plan_by_id(user_id, day_id, number)

    if number:
        reply = "готово"
    else:
        reply = "похоже, планов и так нет.."

    bot.send_message(user_id, reply)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton(text='привет')
    markup.add(btn1)
    bot.send_message(message.chat.id, text="привет, {0.first_name}!!\nя твой малыш чат-бот".format(message.from_user),
                     reply_markup=markup)

@bot.message_handler(commands=['stop'])
def stoppen(message):
    markup = telebot.types.ReplyKeyboardRemove()
    bot.reply_to(message, "вы остановили меня", reply_markup=markup)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    global waiting_for_title, markup
    global waiting_for_text
    global current_note_title
    global current_note_antwort
    global current_note_antwort2
    global current_note_antwort1
    global current_plan
    global current_day
    global waiting_for_antwort
    global waiting_for_antwort1
    global waiting_for_antwort2
    global waiting_for_plan_text1
    global waiting_for_plan_text2
    global waiting_for_plan


    if message.text == '/start':
        start(message)
    elif message.text == '/stop':
        stoppen(message)
    elif 'привет' in message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(text='создать заметку')
        btn2 = types.KeyboardButton(text='мои заметки')
        btn3 = types.KeyboardButton(text='добавить план')
        btn4 = types.KeyboardButton(text='показать все планы')
        btn5 = types.KeyboardButton(text='поменять планы')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.reply_to(message, "что ты хочешь сделать?", reply_markup=markup)
    elif 'создать заметку' in message.text:
        waiting_for_title = True
        bot.send_message(message.chat.id, "введите название заметки:")
    elif waiting_for_title:
        current_note_title = message.text
        waiting_for_title = False
        waiting_for_text = True
        bot.send_message(message.chat.id, "введите текст заметки:")
    elif waiting_for_text:
        note_text = message.text
        user_id = message.chat.id
        add_note(user_id, current_note_title, note_text)
        waiting_for_text = False
        bot.send_message(message.chat.id, "заметка добавлена!")
    elif 'мои заметки' in message.text:
        user_id = message.chat.id
        notes = get_user_notes(user_id)
        if len(notes) > 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(text='создать заметку')
            btn2 = types.KeyboardButton(text='мои заметки')
            btn3 = types.KeyboardButton(text='открыть заметку')
            btn4 = types.KeyboardButton(text='удалить заметку')
            btn5 = types.KeyboardButton(text='добавить план')
            btn6 = types.KeyboardButton(text='показать все планы')
            btn7 = types.KeyboardButton(text='поменять планы')
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            reply = "ваши заметки :\n"
            for i, note in enumerate(notes, start=1):
                reply += f"{i}. {note}\n"

        else:
            reply = "у вас пока нет заметок."

        bot.send_message(message.chat.id, reply, reply_markup=markup)
    elif 'открыть заметку' in message.text:
        waiting_for_antwort = True
        bot.send_message(message.chat.id, "выберите название заметки")
    elif waiting_for_antwort:
        user_id = message.chat.id
        current_note_antwort = message.text
        open_note_id_handler(user_id, current_note_antwort)
        waiting_for_antwort = False

    elif 'удалить заметку' in message.text:
        waiting_for_antwort1 = True
        bot.send_message(message.chat.id, "выберите название заметки")
    elif waiting_for_antwort1:
        user_id = message.chat.id
        current_note_antwort1 = message.text
        delete_note_id_handler(user_id, current_note_antwort1)
        waiting_for_antwort1 = False

    elif 'назад' in message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(text='создать заметку')
        btn2 = types.KeyboardButton(text='мои заметки')
        btn3 = types.KeyboardButton(text='добавить план')
        btn4 = types.KeyboardButton(text='показать все планы')
        btn5 = types.KeyboardButton(text='поменять планы')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.reply_to(message, "что ты хочешь сделать?", reply_markup=markup)

    elif 'показать все планы' in message.text:
        user_id = message.chat.id
        open_plan_id_handler(user_id, 'понедельник')
        open_plan_id_handler(user_id, 'вторник')
        open_plan_id_handler(user_id, 'среда')
        open_plan_id_handler(user_id, 'четверг')
        open_plan_id_handler(user_id, 'пятница')
        open_plan_id_handler(user_id, 'суббота')
        open_plan_id_handler(user_id, 'воскресенье')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(text='назад')
        btn2 = types.KeyboardButton(text='поменять планы')
        markup.add(btn1, btn2)
        bot.reply_to(message, "что ты хочешь сделать?", reply_markup=markup)

    elif 'добавить план' in message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item_mo = types.KeyboardButton(text='понедельник')
        item_tu = types.KeyboardButton(text='вторник')
        item_we = types.KeyboardButton(text='среда')
        item_th = types.KeyboardButton(text='четверг')
        item_fr = types.KeyboardButton(text='пятница')
        item_sa = types.KeyboardButton(text='суббота')
        item_su = types.KeyboardButton(text='воскресенье')
        item_back = types.KeyboardButton(text='назад')
        markup.add(item_mo, item_tu, item_we, item_th, item_fr, item_sa, item_su, item_back)
        waiting_for_plan_text1 = True
        bot.reply_to(message, "на какой день недели?", reply_markup=markup)
    elif waiting_for_plan_text1:
        current_day = message.text
        waiting_for_plan_text1 = False
        waiting_for_plan = True
        bot.send_message(message.chat.id, "добавьте задачу")
    elif waiting_for_plan:
        plan = message.text
        user_id = message.chat.id
        add_plan(user_id, current_day, plan)
        waiting_for_plan = False
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item_new = types.KeyboardButton(text='добавить план')
        item_back = types.KeyboardButton(text='назад')
        item_show_all = types.KeyboardButton(text='показать все планы')
        markup.add(item_new, item_back, item_show_all)
        bot.reply_to(message, "готово", reply_markup=markup)

        #вывод дня сразу же
        open_plan_id_handler(user_id, current_day)


    elif 'поменять планы' in message.text:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        item_mo = types.KeyboardButton(text='понедельник')
        item_tu = types.KeyboardButton(text='вторник')
        item_we = types.KeyboardButton(text='среда')
        item_th = types.KeyboardButton(text='четверг')
        item_fr = types.KeyboardButton(text='пятница')
        item_sa = types.KeyboardButton(text='суббота')
        item_su = types.KeyboardButton(text='воскресенье')
        item_back = types.KeyboardButton(text='назад')
        markup.add(item_mo, item_tu, item_we, item_th, item_fr, item_sa, item_su, item_back)
        waiting_for_plan_text2 = True
        bot.reply_to(message, "на какой день недели?", reply_markup=markup)
    elif waiting_for_plan_text2:
        user_id = message.chat.id
        current_day = message.text
        waiting_for_plan_text2 = False
        open_plan_id_handler(user_id, current_day)
        waiting_for_antwort2 = True
        bot.send_message(message.chat.id, "введите номер выполненной задачи")
    elif waiting_for_antwort2:
        user_id = message.chat.id
        current_note_antwort2 = message.text
        delete_plan_id_handler(user_id, current_day, current_note_antwort2)
        waiting_for_antwort2 = False
        open_plan_id_handler(user_id, current_day)


    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(text='создать заметку')
        btn2 = types.KeyboardButton(text='мои заметки')
        btn3 = types.KeyboardButton(text='добавить план')
        btn4 = types.KeyboardButton(text='показать все планы')
        btn5 = types.KeyboardButton(text='поменять планы')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.reply_to(message, "что ты хочешь сделать?", reply_markup=markup)


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    bot.reply_to(message, "wow")


create_table()
create_table_todolist()

while True:
    try:
        bot.polling()
    except Exception as e:
        # Обработка исключения и возможные действия в случае ошибки
        print(e)
        time.sleep(5)
