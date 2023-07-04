import telebot
import db
from telebot import types

bot = telebot.TeleBot('6086054957:AAEeQHfrsHjywhKS1p9H-YrQc-nkLNcWZ0g')

# TODO  Инициализировать словарь, который будет хранить объекты User, таким образом не будет пересечений в работе бота
class User:
    def __init__(self):
        self.user_id = None
        self.name = None
        self.surname = None
        
        self.new_user = True

    def get_user_data(self):
        '''
        Возвращает данные пользователя
        '''
        return self.user_id, self.name, self.surname


    def db_init(self, force=False):
        '''
        Инициализирует БД
        force - Уничтожает таблицы в БД и создает новые
        '''
        db.init_user_db()
        db.init_user_db()

    
    def check_user_in_db(self):
        '''
        Проверяет наличие пользователя в БД
        '''
        if db.check_id_in_db(self.user_id, 'user_data'):
            self.name, self.surname = db.get_user_data_from_db(self.user_id)
            return True
        return False


    def save_user_in_db(self):
        '''
        Добавляет нового пользователя в БД
        '''
        db.add_user_to_db(self.get_user_data())


    def replace_user_in_db(self, replace_column: str, replace_value):
        '''
        Заменяет значение на replace_value в столбце replace_column БД 
        '''
        pass

def run_telegram_bot():
    user = User()

    @bot.message_handler(commands=['registration'])
    def registration(message):
        if user.user_id is None:
            user.user_id = message.chat.id
        if user.new_user:
            bot.send_message(user.user_id, 'Перед использованием нажмите /start')
            return
        if user.check_user_in_db():
            bot.send_message(user.user_id, 'Я вас узнал, {} {}. Введите /help, если не помните список команд'.format(user.name, user.surname))
            return
        bot.send_message(user.user_id, 'Введите свое имя.')
        bot.register_next_step_handler(message, get_name)

    @bot.message_handler(commands=['start'])
    def start(message):
        user = User()
        user.new_user = False
        user.db_init()
        if user.user_id is None:
            user.user_id = message.chat.id
        if user.check_user_in_db():
            # Такой пользователь есть в БД
            bot.send_message(user.user_id, '{} {}, приятно вас снова видеть!\nВведите команду, которую необходимо исполнить.'.format(
                user.name, user.surname
            ))
            bot.send_message(user.user_id, 'Если вы не помните список нужных команд, то напишите: /help')
        else:
            bot.send_message(user.user_id, 'Начнем процесс регистрации. Введите /registration')

    @bot.message_handler(commands=['help'])
    def help(message):
        if user.user_id is None:
            user.user_id = message.chat.id
        if user.new_user:
            bot.send_message(user.user_id, 'Перед началом использования нажмите /start')
            return

        if user.check_user_in_db():
            # Ввыодим список текущих команд
            bot.send_message(user.user_id, ';d;d;d;d;')
        else:
            bot.send_message(user.user_id, 'Введите /start')

    '''
    @bot.message_handler(content_types=['text'])
    def main(message):
        # Проверить, что пользователь есть в базе
        pass
    '''

    def get_name(message):
        user.name = message.text
        bot.send_message(user.user_id, 'Какая у тебя фамилия?')
        bot.register_next_step_handler(message, get_surname)

    def get_surname(message):
        user.surname = message.text
        bot.send_message(user.user_id, 'Внимание! Последний вопрос')
        keyboard = types.InlineKeyboardMarkup() #наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes') #кнопка «Да»
        keyboard.add(key_yes) #добавляем кнопку в клавиатуру
        key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Вас зовут {} {}?'.format(user.name, user.surname)
        bot.send_message(user.user_id, text=question, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
            user.save_user_in_db()
            bot.send_message(user.user_id, 'Запомнил!')
        elif call.data == "no":
            bot.send_message(user.user_id, 'Странно, попробуем еще раз. Напиши /registration')

    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    run_telegram_bot()