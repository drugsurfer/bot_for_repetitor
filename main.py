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
        self.user_id = id
        self.name = ''
        self.surname = ''
        self.first_registration = True

    def db_init(self):
        pass

user = User()
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        global user
        user.user_id = message.chat.id
        bot.send_message(message.chat.id, 'Давай познакомимся. Меня зовут Кринж-Лорд! А как тебя именуют?')
        bot.register_next_step_handler(message, get_name) #следующий шаг – функция get_name
    else:
        bot.send_message(message.chat.id, 'УРОД, напиши /start')

def get_name(message):
    global user
    user.name = message.text
    bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global user
    if user.first_registration:
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
