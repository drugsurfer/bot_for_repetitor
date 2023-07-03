import telebot
import db
from telebot import types

bot = telebot.TeleBot('6086054957:AAEeQHfrsHjywhKS1p9H-YrQc-nkLNcWZ0g')

'''
name = '';
surname = '';
age = 0;
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Как тебя зовут?");
        bot.register_next_step_handler(message, get_name); #следующий шаг – функция get_name
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg');

def get_name(message): #получаем фамилию
    global name;
    name = message.text;
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?');
    bot.register_next_step_handler(message, get_surname);

def get_surname(message):
    global surname;
    surname = message.text;
    bot.send_message(message.from_user.id, 'Сколько тебе лет?');
    bot.register_next_step_handler(message, get_age);

def get_age(message):
    global age;
    while age == 0: #проверяем что возраст изменился
        try:
            age = int(message.text) #проверяем, что возраст введен корректно
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes'); #кнопка «Да»
        keyboard.add(key_yes); #добавляем кнопку в клавиатуру
        key_no= types.InlineKeyboardButton(text='Нет', callback_data='no');
        keyboard.add(key_no);
        question = 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?';
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Запомню : )');
    elif call.data == "no":
        bot.send_message(call.message.from_user.id, 'Напиши /reg');

bot.polling(none_stop=True, interval=0)
#bot.infinity_polling()

'''

class User:
    def __init__(self):
        self.user_id = None
        self.name = None
        self.surname = None
        self.first_registration = True

    def db_init(self, force=False):
        '''
        Инициализирует БД
        force - Уничтожает таблицы в БД и создает новые
        '''
        db.init_user_db()
        db.init_user_db()
    
    def check_user_in_db(self):
        if db.check_id_in_db(user.user_id, 'user_data'):
            self.first_registration, self.name, self.surname = False, db.get_user_data_from_db(user.user_id)
            return True
        return False


user = User()

@bot.message_handler(commands=['registration'])
def registration(message):
    bot.send_message(message.chat.id, message.chat.id)

@bot.message_handler(commands=['start'])
def start(message):
    # При запуске бота выполняется этот метод! Нет проверки наличия пользователя в БД
    global user
    if user.user_id is None:
        user.user_id = message.chat.id
    if user.check_user_in_db():
        # Такой пользователь есть в БД
        bot.send_message(user.user_id, '{} {}, приятно вас снова видеть!\nВведите команду, которую необходимо исполнить.'.format(
            user.name, user.surname
        ))
        bot.send_message(user.user_id, 'Если вы не помните список нужных команд, то напишите: /help')
    else:
        bot.send_message(user.user_id, 'Начнем процесс регистрации. Введите свое имя')
        bot.register_next_step_handler(message, get_name)

@bot.message_handler(commands=['help'])
def help(message):
    global user
    if not user.first_registration:
        # Ввыодим список текущих команд
        bot.send_message(user.user_id, '')
    else:
        bot.send_message(message.chat.id, 'Воспользуйтесь регистрацией через /start')

@bot.message_handler(content_types=['text'])
def main(message):
    # Проверить, что пользователь есть в базе
    global user
    user.user_id = str(message.chat.id)
    user.db_init()
    if db.check_id_in_db(user.user_id, 'user_data'):
        # Такой преподаватель есть в базе
        user.first_registration, user.name, user.surname = False, db.get_user_data_from_db(user.user_id)
        bot.send_message(user.user_id, '{} {}, приятно вас снова видеть!\nВведите команду, которую необходимо исполнить.'.format(
            user.name, user.surname
        ))
        bot.send_message(user.user_id, 'Если вы не помните список нужных команд, то напишите: /help')
    else:
        bot.send_message(user.user_id, 'Мы еще не знакомы. Если ты готов познакомиться напиши: /start')


def get_name(message):
    global user
    user.name = message.text
    bot.send_message(user.user_id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global user
    user.surname = message.text
    #bot.send_message(message.chat.id, 'Внимание! Последний вопрос')
    keyboard = types.InlineKeyboardMarkup() #наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes') #кнопка «Да»
    keyboard.add(key_yes) #добавляем кнопку в клавиатуру
    key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    if user.first_registration:
        question = 'Правильно я понял, тебя зовут ананист89 и твоя фамилия сталкер-паркур?'
    else:
        question = 'Правильно я понял, тебя зовут ' + user.name + ' и твоя фамилия ' + user.surname
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global user
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Запомню!')
    elif call.data == "no":
        if user.first_registration:
            user.first_registration = False
            bot.send_message(call.message.chat.id, 'Да я угараю! Попробуем еще раз?')
            bot.register_next_step_handler(call.message, get_surname)
        else:
            bot.send_message(call.message.chat.id, 'Странно, попробуем еще раз. Напиши /reg')


bot.polling(none_stop=True, interval=0)
