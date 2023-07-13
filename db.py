import sqlite3
import datetime

__connection = None

def get_connection():
    '''
    Проверяет соединение с базой
    '''
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('rep.db',check_same_thread=False)
    return __connection

def init_user_db(force: bool = False):
    '''
    инициализирует таблицу преподавателей. force может перезаписать старую
    '''
    connection = get_connection()
    c = connection.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS user_data')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id_primary          INTEGER PRIMARY KEY,
            id     INTEGER NOT NULL,
            name   TEXT NOT NULL,
            sur_name TEXT NOT NULL);
    ''')

    connection.commit()

def init_students_db(force: bool = False):
    '''
    инициализирует таблицу учеников. force может перезаписать старую
    user_id -> id FROM user_data

    '''
    connection = get_connection()
    c = connection.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS students')

    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id_primary          INTEGER PRIMARY KEY,
            id INTEGER NOT NULL,
            name   TEXT NOT NULL,
            sur_name TEXT NOT NULL,
            science_object TEXT NOT NULL,
            lesson_cost INTEGER NOT NULL,
            date_next_lesson TEXT NOT NULL);
    ''')

    connection.commit()

def init_lessons_db(force: bool = False):
    '''
    Инициализирует таблицу уроков
    id -> id_primary FROM students
    '''
    connection = get_connection()
    c = connection.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS lessons')

    c.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id_primary INTEGER PRIMARY KEY,
            id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_lesson TEXT NOT NULL);
    ''')

    connection.commit()

def add_lesson_to_db(student_id: int, time_lesson: str, date_next_lesson: str):
    '''
    Добавляет в lessons запись урока
    student_id - id_primary ученика from students
    time_lesson - длительность урока в часах
    date_next_lesson - (day, month, year next_lesson)
    time_next_lesson - (hour, minutes next_lesson)
    '''
    connection = get_connection()
    c = connection.cursor()
    if check_student_in_db(student_id):
        now_data = str(datetime.datetime.now()).split() # ['2022-06-20', '16:06:13.176788']
        date = now_data[0] + '-' + now_data[1][:5]
        c.execute(
            'INSERT INTO lessons (id, date, time_lesson) VALUES (?, ?, ?);',
            (student_id, date, time_lesson)
        )
        replace_value(date_next_lesson, 'date_next_lesson', 'students', student_id)
    connection.commit()

def check_student_in_db(id: int):
    '''
    Проверяет наличие ученика с id_primary в таблице students
    '''
    connection = get_connection()
    c = connection.cursor()
    if len(c.execute(
        'SELECT * FROM STUDENTS WHERE id_primary = ?;',
        (id, )).fetchall()) != 0:
        return True
    return False


def add_user_to_db(user: tuple):
    '''
    Добавляет в user_data запись пользователя
    user = (id: str, name: str, surname: str)
    '''
    connection = get_connection()
    c = connection.cursor()
    if not check_id_in_user_db(user[0], 'user_data'):
        c.execute('INSERT INTO user_data (id, name, sur_name) VALUES (?, ?, ?);', (user[0], user[1], user[2]))
    connection.commit()

def get_student_in_db(user_id: str, student_name: str, student_science: str):
    '''
    Ищет ученика по определенному критерию
    user_id - id преподавателя, среди учеников которого происходит поиск
    student_name - имя ученика
    student_science - предмет, которым занимается ученик
    '''
    connection = get_connection()
    c = connection.cursor()
    return c.execute(
        'SELECT * FROM students WHERE id = ? AND name = ? AND science_object = ?', 
        (user_id, student_name, student_science)
        ).fetchall()

def get_all_students_fot_user(user_id: str):
    '''
    Возвращает всех студентов, прикрепленных к текущему преподавателю
    '''
    connection = get_connection()
    c = connection.cursor()
    return c.execute(
        'SELECT * FROM students WHERE id = ?', 
        (user_id, )).fetchall()

def get_user_data_from_db(user_id: str):
    '''
    Возвращает информацию о преподавателе
    return: (user_name, user_surname)
    '''
    connection = get_connection()
    c = connection.cursor()
    data = c.execute(
        'SELECT * FROM user_data WHERE id = ?;', 
        (user_id, )
        ).fetchall()[0]
    return data[2], data[3]

def add_student_to_db(student: tuple):
    '''
    Добавляет ученика в students.
    student = (user_id: int, name: str, sur_name: str, science_object: str, lesson_cost: int, date_next_lesson: str)
    '''
    user_id, name, sur_name, science_object, lesson_cost, date_next_lesson = student
    connection = get_connection()
    c = connection.cursor()
    if check_id_in_user_db(user_id, 'user_data'):
        # преподаватель ученика есть в базе
        if len(get_student_in_db(user_id, name, science_object)) == 0:
            c.execute(
                'INSERT INTO students (id, name, sur_name, science_object, lesson_cost, date_next_lesson) VALUES (?, ?, ?, ?, ?, ?);',
                (user_id, name, sur_name, science_object, lesson_cost, date_next_lesson)
            )
        else:
            print(name, 'уже есть в таблице students')
    else:
        # ну каким-то волшебным образом не будет преподавателя в базе
        pass
    connection.commit()

def del_student_to_db(student_id: int):
    '''
    Удаляет ученика из таблицы students, по id_primary (student_id)
    '''
    # TODO: Добавить удаление всех уроков с этим учеником в БД
    connection = get_connection()
    c = connection.cursor()
    c.execute(
        'DELETE FROM students WHERE id_primary = ?;',
        (student_id,)
    )
    connection.commit()

def check_id_in_user_db(id: int, db_name: str):
    connection = get_connection()
    c = connection.cursor()
    if c.execute('SELECT EXISTS (SELECT 1 FROM {} WHERE id = ? LIMIT 1);'.format(db_name), (id, )).fetchone()[0]:
        return True # такой id уже есть в БД
    else:
        # такого id нет в БД
        return False

def check_table_in_db(table_name: str) -> bool:
    '''
    Проверяет наличие таблицы в базе
    '''
    connection = get_connection()
    c = connection.cursor()
    if c.execute('SELECT count(*) FROM sqlite_master WHERE type = "table" AND name = ?;', (table_name,)):
        return True
    else:
        return False

def replace_value(value, column_name: str, table_name: str, id: int):
    '''
    Заменяет переданное значение value в переданном столбце column_name
    table_name - название таблицы
    id - id записи (PRIMARY KEY only)
    '''
    connection = get_connection()
    c = connection.cursor()
    # Проверка наличия таблицы в БД
    if check_table_in_db(table_name):
        try:
            c.execute('UPDATE {} SET {} = ? WHERE id_primary = {}'.format(table_name, column_name, id), (value, ))
        except:
            print('Не удалось обновить значение в таблице ', table_name)
    else:
        print('Не найдена таблица ', table_name)
    connection.commit()

def check_db():
    connection = get_connection()
    c = connection.cursor()
    c.execute('SELECT * FROM user_data;')
    print(c.fetchall())

if __name__ == '__main__':
    init_user_db()
    init_students_db()
    init_lessons_db()