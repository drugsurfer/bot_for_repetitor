import telebot
import db
from telebot import types

bot = telebot.TeleBot('6086054957:AAEeQHfrsHjywhKS1p9H-YrQc-nkLNcWZ0g')

users = {} # Словарь, хранящий текущих пользователей

# TODO Удаление через primary key нереально. Придумать другое удаление 

class User:
    def __init__(self, id: str):
        self.user_id = id
        self.name = None
        self.surname = None

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
        print(self.get_user_data())
        db.add_user_to_db(self.get_user_data())

    def del_student(self, student_id: int, students: list):
        '''
        Удаляет студента из БД по его id_primary
        '''
        id_ = students[student_id][0]
        try:
            db.del_student_to_db(id_)
            return True
        except Exception:
            return False

    def get_student(self, student_name: str = None, student_science: str = None):
        '''
        Возвращает всех учеников, прикрепленных к текущему user
        if student_name == None or student_science == None -> all_students
        else -> student
        '''
        if student_name == None or student_science == None:
            student = db.get_all_students_fot_user(self.user_id)
        else:
            student = db.get_student_in_db(self.user_id, student_name, student_science)
        return student

    def add_student_in_db(self, name, surname, science, cost):
        '''
        Добавляет нового ученика в БД 
        '''
        db.add_student_to_db((self.user_id, name, surname, science, cost))

    def add_lesson_to_db(self, student_id, time_lesson, time_next_lesson):
        '''
        Сохраняет информацию о проведенном и новом уроке в БД
        '''
        pass

    def replace_user_in_db(self, replace_column: str, replace_value):
        '''
        Заменяет значение на replace_value в столбце replace_column БД 
        '''
        pass


def check_user_is_auth(id: str):
    '''
    Проверяет, что пользователь уже был в текущей сессии бота. 
    Если был -> сохраненные данные
    Если нет -> созданный объект User
    '''
    if id not in users.keys():
        user = User(id)
        users[id] = user
    else: 
        user = users[id]
    return user


def run_telegram_bot():

    @bot.message_handler(commands=['add_lesson'])
    def add_lesson(message):
        user = check_user_is_auth(str(message.chat.id))
        if not user.check_user_in_db():
            bot.send_message(
                user.user_id,
                'Вы еще не зарегистрированы. Нажмите /start'
            )
            return
        bot.send_message(
            user.user_id,
            'Введите номер ученика, с которым у вас был урок, а также сколько по времени длился урок (в часах) в формате:\n\
1. Номер ученика из списка.\n\
2. Количество в часах.\n\
3. Время следующего урока в формате: день - месяц - время урока. Например: 07 - 11 - 17:00.')
        # TODO Переписать, потому что теперь ученики выводятся в формате кнопок
        show_info_for_students(user)
        bot.register_next_step_handler(message, add_lesson_in_db)

    def add_lesson_in_db(message):
        user = check_user_is_auth(str(message.chat.id))
        parse_str = message.text.split('\n')
        try:
            student_id = int(parse_str[0].split('.')[1])
            time_lesson = int(parse_str[1].split('.')[1])
            date_next_lesson = parse_str[2].split('.')[1]
        except Exception:
            bot.send_message(
                user.user_id, 
                'Неправильно введены данные. Смотри внимательнее пример.'
                )

    @bot.message_handler(commands=['del_student'])
    def del_student(message):
        user = check_user_is_auth(str(message.chat.id))
        if not user.check_user_in_db():
            bot.send_message(
                user.user_id,
                'Вы еще не зарегистрированы. Нажмите /start'
            )
            return
        show_info_for_students(user, del_message=True)
        #bot.register_next_step_handler(message, del_student_from_db)

    @bot.message_handler(commands=['add_new_student'])
    def add_new_student(message):
        user = check_user_is_auth(str(message.chat.id))
        if not user.check_user_in_db():
            bot.send_message(
                user.user_id,
                'Вы еще не зарегистрированы. Нажмите /start'
            )
            return
        bot.send_message(
            user.user_id,
            'Введите данные ученика: в следующем порядке:\
            \n1. Имя\
            \n2. Фамилия\
            \n3. Предмет\
            \n4. Стоимость урока'
        )
        bot.register_next_step_handler(message, add_student_in_db)

    def add_student_in_db(message):
        user = check_user_is_auth(str(message.chat.id))
        # TODO Переписать адекватный парсер
        # TODO Добавить кнопки ДА/НЕТ и только потом добавлять в базу
        parse_str = message.text.split('\n')
        student_data = []
        for i, s in enumerate(parse_str):
            if str(i + 1) not in s:
                bot.send_message(
                    user.user_id, 
                    'Неправильно введены данные ученика. Смотри внимательнее пример!'
                )
                return
            student_data.append(s.split('.')[1].split()[0])
        try:
            user.add_student_in_db(*student_data)
            bot.send_message(
                user.user_id, 
                'Ученик добавлен!'
            )
        except Exception:
            bot.send_message(
                user.user_id, 
                'Проблемы с добавлением в БД. Попробуйте еще раз!'
            )

    @bot.message_handler(commands=['all_info_for_students'])
    def all_info_for_students(message):
        user = check_user_is_auth(str(message.chat.id))
        if not user.check_user_in_db():
            bot.send_message(
                user.user_id,
                'Вы еще не зарегистрированы. Нажмите /start'
            )
            return
        # TODO Здесь можно добавить параллельную ветку. Выводятся все ученики 
        # а далее вызывается меню в котором можно выбрать что делать с учеником
        show_info_for_students(user)

    def show_info_for_students(user: User, del_message: bool = False):
        '''
        Выводит информацию об учениках, в виде кнопок
        '''
        students = user.get_student()
        if len(students) == 0:
            bot.send_message(
                user.user_id,
                'На данный момент, к вам не прикрепленны ученики. \
                Для добавления ученика нажмите /add_new_student.'
            )
            return
        '''
        message_ = ''
        for i, student in enumerate(students):
            name_, surname_, science_, cost_ = student[2], student[3], student[4], student[5]
            message_ += f'{i + 1}. {name_} {surname_}. Предмет: {science_}. Стоимость урока: {cost_}р.\n'
        bot.send_message(
            user.user_id,
            message_
        )
        if del_message:
            bot.send_message(
                user.user_id,
                'Введите номер ученика'
            )
        '''
        keyboard = types.InlineKeyboardMarkup()
        for i, student in enumerate(students):
            name, surname = student[2], student[3]
            if del_message:
                data = f'del_student-{i}'
            key = types.InlineKeyboardButton(text=f'{name} {surname}', callback_data=data)
            keyboard.add(key)
        if del_message:
            bot.send_message(
            user.user_id, 
            text='Выберите удаляемого ученика', 
            reply_markup=keyboard
        )

    @bot.message_handler(commands=['registration'])
    def registration(message):
        user = check_user_is_auth(str(message.chat.id))
        if user.check_user_in_db():
            bot.send_message(
                user.user_id, 
                f'Я вас узнал, {user.name} {user.surname}. Введите /help, если не помните список команд')
            return
        bot.send_message(user.user_id, 'Введите свое имя.')
        bot.register_next_step_handler(message, get_name)

    @bot.message_handler(commands=['start'])
    def start(message):
        user = check_user_is_auth(str(message.chat.id))
        if user.check_user_in_db():
            # Такой пользователь есть в БД
            bot.send_message(
                user.user_id, 
                f'{user.name} {user.surname}, приятно вас снова видеть!\nВведите команду, которую необходимо исполнить.'
            )
            bot.send_message(
                user.user_id, 
                'Если вы не помните список нужных команд, то напишите: /help'
            )
        else:
            bot.send_message(
                user.user_id, 
                'Начнем процесс регистрации. Введите /registration'
            )

    @bot.message_handler(commands=['help'])
    def help(message):
        user = check_user_is_auth(str(message.chat.id))
        if user.check_user_in_db():
            # Ввыодим список текущих команд
            bot.send_message(
                user.user_id, 
                "/registration - запустить процесс регистрации;\n\
/all_info_for_students - показать информацию о текущих учениках;\n\
/replace_info_about_student - заменить информацию о ученике;\n\
/add_new_student - добавить нового ученика;\n\
/del_student - удалить ученика;\n\
/add_lesson - добавить урок;\n\
/stat_for_week - вывести статистику за текущую неделю;\n\
/stat_for_month - вывести статистику за текущий месяц;"
            )
        else:
            bot.send_message(
                user.user_id,
                'Сначала познакомимся. Введите /start'
            )

    def get_name(message):
        user = check_user_is_auth(str(message.chat.id))
        user.name = message.text
        bot.send_message(
            user.user_id, 
            'Какая у тебя фамилия?'
        )
        bot.register_next_step_handler(message, get_surname)

    def get_surname(message):
        user = check_user_is_auth(str(message.chat.id))
        print(message.chat.id)
        user.surname = message.text
        bot.send_message(
            user.user_id, 
            'Внимание! Последний вопрос'
        )
        keyboard = types.InlineKeyboardMarkup() #наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes') #кнопка «Да»
        keyboard.add(key_yes) #добавляем кнопку в клавиатуру
        key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = f'Вас зовут {user.name} {user.surname}?'
        bot.send_message(
            user.user_id, 
            text=question, 
            reply_markup=keyboard
        )
            
    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        user = check_user_is_auth(str(call.message.chat.id))
        print(call.message.chat.id)
        if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
            user.save_user_in_db()
            bot.send_message(
                user.user_id, 
                'Запомнил!'
            )
        elif call.data == "no":
            bot.send_message(
                user.user_id, 
                'Странно, попробуем еще раз. Напиши /registration'
            )
        command = call.data.split('-')[0]
        if command == 'del_message':
            student_id = int(call.data.split('-')[1])
            students = user.get_student()
            if user.del_student(student_id, students):
                bot.send_message(
                    user.user_id,
                    'Успешно!'
                )
            else:
                bot.send_message(
                    user.user_id,
                    'Проблемы с БД. Попробуйте позже.'
                )

        bot.answer_callback_query(call.id)

    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    run_telegram_bot()