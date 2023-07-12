import telebot
import db
from telebot import types

bot = telebot.TeleBot('6086054957:AAEeQHfrsHjywhKS1p9H-YrQc-nkLNcWZ0g')

users = {} # Словарь, хранящий текущих пользователей

class User:
    def __init__(self, id: str):
        self.user_id = id
        self.name = None
        self.surname = None
        self.lesson_info = [] # [student_id, time_lesson, (day, month, year next_lesson), (hour, minutes next_lesson)]

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
        if db.check_id_in_user_db(self.user_id, 'user_data'):
            self.name, self.surname = db.get_user_data_from_db(self.user_id)
            return True
        return False

    def save_user_in_db(self):
        '''
        Добавляет нового пользователя в БД
        '''
        print(self.get_user_data())
        db.add_user_to_db(self.get_user_data())

    def del_student(self, student_id: int):
        '''
        Удаляет студента из БД по его id_primary
        '''
        students = self.get_student()
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

    def add_lesson_to_db(self):
        '''
        Сохраняет информацию о проведенном и новом уроке в БД
        '''
        students = self.get_student()
        id_ = students[self.lesson_info[0]][0]

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
        show_info_for_students(user, add_message=True)

    def get_time_lesson(message):
        user = check_user_is_auth(str(message.chat.id))
        user.lesson_info.append(message.text)
        bot.send_message(
            user.user_id,
            'Введите дату следующего урока в формате: day-month-year-hour:minute. Например: 12-06-2023-15:00'
        )
        bot.register_next_step_handler(message, get_date_next_lesson)

    def get_date_next_lesson(message):
        user = check_user_is_auth(str(message.chat.id))
        try:
            day, month, year, time = message.text.split('-')
            answer = None
            if not(1 <= int(day) <= 31):
                answer = 'День введен некорректно!'
            if not(1 <= int(month) <= 12):
                answer = 'Месяц введен некорректно!'
            if len(year.split()[0]) != 4:
                answer = 'Год введен некорректно!'
            hour, minutes = time.split(':')
            if not(0 <= int(hour) <= 12):
                answer = 'Час введен некорректно!'
            if not(0 <= int(minutes) <= 59):
                answer = 'Минуты введены некорректно!'
            if answer is not None:
                bot.send_message(
                    user.user_id,
                    answer
                )
            else:
                user.lesson_info.append((day.split()[0], hour.split()[0], year.split()[0]))
                user.lesson_info.append((hour.split()[0], minutes.split()[0]))
                add_lesson_to_db(user)
        except Exception:
            bot.send_message(
                user.user_id,
                'Неправильно введено время следующего урока, попробуйте еще раз. Нажмите /add_lesson'
            )

    def add_lesson_to_db(user):
        try:
            user.add_lesson_to_db()
            bot.send_message(
                user.user_id,
                'Урок успешно добавлен!'
            )
        except Exception:
            bot.send_message(
                user.user_id,
                'Проблемы с добавлением в БД! Попробуйте позже.'
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
        keyboard = types.InlineKeyboardMarkup()
        data = 'add_student'
        key = types.InlineKeyboardButton(
            text='Да, все верно', 
            callback_data=(data + f'-yes-{student_data[0]}-{student_data[1]}-{student_data[2]}-{student_data[3]}')
            )
        keyboard.add(key)
        key = types.InlineKeyboardButton(text='Нет', callback_data=(data + '-no'))
        keyboard.add(key)
        bot.send_message(
            user.user_id, 
            text=f'''Правильно я понял данные нового ученика:
1. {student_data[0]};
2. {student_data[1]};
3. {student_data[2]};
4. {student_data[3]}.''', 
            reply_markup=keyboard
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
        show_info_for_students(user, list_view=True)

    def show_info_for_students( user: User, 
                                list_view: bool = False,
                                del_message: bool = False,
                                add_message: bool = False):
        '''
        Выводит информацию об учениках
        '''
        students = user.get_student()
        if len(students) == 0:
            bot.send_message(
                user.user_id,
                'На данный момент, к вам не прикрепленны ученики. \
                Для добавления ученика нажмите /add_new_student.'
            )
            return
        if list_view:
            message_ = ''
            for i, student in enumerate(students):
                name_, surname_, science_, cost_ = student[2], student[3], student[4], student[5]
                message_ += f'{i + 1}. {name_} {surname_}. Предмет: {science_}. Стоимость урока: {cost_}р.\n'
            bot.send_message(
                user.user_id,
                message_
            )
            return
        keyboard = types.InlineKeyboardMarkup()
        for i, student in enumerate(students):
            name, surname = student[2], student[3]
            if del_message:
                data = f'del_student-{i}'
            if add_message:
                data = f'add_lesson-{i}'
            key = types.InlineKeyboardButton(text=f'{name} {surname}', callback_data=data)
            keyboard.add(key)
        if del_message:
            bot.send_message(
                user.user_id, 
                text='Выберите удаляемого ученика', 
                reply_markup=keyboard
            )
        if add_message:
            bot.send_message(
                user.user_id,
                text='Выберите ученика, с которым у вас был урок',
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

        if command == 'del_student':
            student_id = int(call.data.split('-')[1])
            if user.del_student(student_id):
                bot.send_message(
                    user.user_id,
                    'Успешно!'
                )
            else:
                bot.send_message(
                    user.user_id,
                    'Проблемы с БД. Попробуйте позже.'
                )

        if command == 'add_lesson':
            student_id = int(call.data.split('-')[1])
            user.lesson_info.append(student_id)
            bot.send_message(
                user.user_id,
                'Введите сколько (в часах) длился урок'
            )
            bot.register_next_step_handler(call.message, get_time_lesson)
            
        if command == 'add_student':
            answer = call.data.split('-')
            if answer[1] == 'yes':
                try:
                    user.add_student_in_db(answer[2], answer[3], answer[4], int(answer[5]))
                    bot.send_message(
                        user.user_id, 
                        'Ученик добавлен!'
                    )
                except Exception:
                    bot.send_message(
                        user.user_id, 
                        'Проблемы с добавлением в БД. Попробуйте еще раз!'
                    )
            else:
                bot.send_message(
                user.user_id, 
                'Странно, попробуем еще раз. Напиши /add_new_student'
                )

        bot.answer_callback_query(call.id)

    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    run_telegram_bot()