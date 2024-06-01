import telebot
import sqlite3
import random
from telebot import types


bot = telebot.TeleBot("7030716899:AAGTPe3aT7NOz2K93ORwt05a-90TlKtEMvs")


conn = sqlite3.connect('words.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY,
        word TEXT NOT NULL,
        correct_accent TEXT NOT NULL,
        incorrect_accent TEXT NOT NULL,
        phrase TEXT NOT NULL
    )
''')

sample_data = [
    ('досуг', 'досУг', 'дОсуг', 'Позову своих подруг, вместе проведём досУг.'),
    ('кремень', 'кремЕнь', 'крЕмень', 'Бей его хоть целый день - не расколется кремЕнь.'),
    ('мусоропровод', 'мусоропровОд', 'мусоропрОвод', 'Вот ведро, и мусор вот. Мусор - в мусоропровОд.'),
    ('водопровод', 'водопровОд', 'водопрОвод', 'Он задел громоотвод и упал в водопровОд.'),
    ('диспансер', 'диспансЕр', 'диспАнсер', ' Все, кто болеет корью, например, помещены в больничный диспансЕр.'),
    ('локтя', 'лОктя', 'локтЯ', 'Царапинка у лОктя от кошачьего когтя.'),
    ('каталог', 'каталОг', 'кАталог', 'Подарок выбрать мне помог один хороший каталОг.'),
    ('партер', 'партЕр', 'пАртер', 'Лишь зашёл в театр мэр, оглянулся весь партЕр.'),
    ('квартала', 'квартАла', 'квАртала', 'Мы прошли немало — целых два квартАла.'),
    ('свеклы', 'свЁклы', 'свеклЫ', 'Мы у тёти Фёклы ели борщ из свЁклы!'),
    ('еретик', 'еретИк', 'Еретик', 'К Папе Римскому проник в дом какой-то еретИк.'),
]

cursor.executemany('INSERT INTO words (word, correct_accent, incorrect_accent, phrase) VALUES (?, ?, ?, ?)', sample_data)

conn.commit()
conn.close()



def get_random_word():
    conn = sqlite3.connect('words.db')
    cursor = conn.cursor()
    cursor.execute('SELECT word, correct_accent, incorrect_accent, phrase FROM words ORDER BY RANDOM() LIMIT 1')
    word = cursor.fetchone()
    conn.close()
    return word

user_state = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Потренируемся немного?\n Отправь /next, чтобы начать.\n А если сомневаешься, где поставить ударение, просто отправь мне это слово")


@bot.message_handler(commands=['next'])
def send_word(message):
    word_data = get_random_word()
    user_state[message.chat.id] = word_data

    correct_btn = types.InlineKeyboardButton(text=word_data[1], callback_data='correct')
    incorrect_btn = types.InlineKeyboardButton(text=word_data[2], callback_data='incorrect')

    buttons = [correct_btn, incorrect_btn]
    random.shuffle(buttons)

    markup = types.InlineKeyboardMarkup()
    for btn in buttons:
        markup.add(btn)

    bot.send_message(message.chat.id, f"Где поставишь ударение в этом слове: {word_data[0]}?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id in user_state:
        word, correct_accent, incorrect_accent, phrase = user_state[chat_id]

        if call.data == 'correct':
            response = "Вау, супер! Напиши /next, чтобы продолжить."
        else:
            response = f"C этим словом все не так просто.\nПравильно будет вот так: '{correct_accent}'.\nЧтобы тебе было легче запомнить, держи рифму:\n{phrase}\nПиши /next, чтобы продолжить."

        bot.send_message(chat_id, response)
        del user_state[chat_id]


@bot.message_handler(func=lambda message: True)
def send_accent_info(message):
    word_input = message.text.strip().lower()
    conn = sqlite3.connect('words.db')
    cursor = conn.cursor()
    cursor.execute('SELECT word, correct_accent, phrase FROM words WHERE lower(word) = ?', (word_input,))
    word_data = cursor.fetchone()
    conn.close()

    if word_data:
        word, correct_accent, phrase = word_data
        response = f"Правильное ударение: '{correct_accent}'\nЧтобы легче запомнить, держи рифму:\n{phrase}"
    else:
        response = "Извини, я не знаю такого слова. Попробуй другое или напиши /next для нового задания."

    bot.reply_to(message, response)


bot.polling(non_stop=True)

