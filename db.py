import sqlite3

__connection = None

def get_connection():
    '''
    Проверяет соединение с базой
    '''
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('rep.db')
    return __connection

def init_user_db(force: bool = False):
    '''
    инициализирует базу преподавателей. force может перезаписать старую
    '''
    connection = get_connection()
    c = connection.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS user_data')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            user_name   TEXT NOT NULL,
            user_sur_name TEXT NOT NULL);
    ''')

    connection.commit()

def init_students_db(force: bool = False):
    '''
    инициализирует базу учеников. force может перезаписать старую
    user_id - id преподавателя, который отвечает за ученика

    '''
    connection = get_connection()
    c = connection.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS students')

    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name   TEXT NOT NULL,
            sur_name TEXT NOT NULL,
            science_object TEXT NOT NULL);
    ''')

    connection.commit()

def add_user_to_db(user: tuple):
    '''
    Добавляет в user_data запись пользователя
    user = (user_id: int, user_name: str, user_surname: str)
    '''
    connection = get_connection()
    c = connection.cursor()
    if check_id_in_db(user[0], 'user_data'):
        print(user[0], 'Уже есть в базе') # такой user_id уже есть в БД
    else:
        # такого user_id нет в БД
        c.execute('INSERT INTO user_data (user_id, user_name, user_sur_name) VALUES (?, ?, ?);', (user[0], user[1], user[2]))
    connection.commit()

def search_students_in_db(user_id: int, student_name: str, student_science: str):
    '''
    Ищет ученика по определенному критерию
    user_id - id преподавателя, среди учеников которого происходит поиск
    student_name - имя ученика
    student_science - предмет, которым занимается ученик
    '''
    pass

def add_student_to_db(student: tuple):
    '''
    Добавляет ученика в students.
    student = (student_id: int, user_id: int, name: str, sur_name: str, science_object: str)
    '''
    student_id, user_id, name, sur_name, science_object = student
    connection = get_connection()
    c = connection.cursor()
    if check_id_in_db(user_id, 'user_data'):
        # преподаватель ученика есть в базе
        pass
    else:
        # ну каким-то волшебным образом не будет преподавателя в базе
        pass
    connection.commit()

def check_id_in_db(id: int, db_name: str):
    connection = get_connection()
    c = connection.cursor()
    if db_name == 'user_data':
        # КОСТЫЛЬ СДЕЛАТЬ ТАК ЧТОБЫ ВО ВСЕХ ТАБЛИЦА id НАЗЫВАЛСЯ ОДИНАКОВО
        pass
    else:
        pass
    if c.execute('SELECT EXISTS (SELECT 1 FROM {} WHERE user_id = ? LIMIT 1);'.format(db_name), (id, )).fetchone()[0]:
        return True # такой user_id уже есть в БД
    else:
        # такого user_id нет в БД
        return False

def check_db():
    connection = get_connection()
    c = connection.cursor()
    c.execute('SELECT * FROM user_data;')
    print(c.fetchall())

init_user_db()
check_db()
add_user_to_db((43333000, 'Евгений', 'Кондратьев'))
add_user_to_db((43333333400, 'Евгений', 'Кондратьев'))
add_user_to_db((43333000, 'Евгений', 'Кондратьев'))
add_user_to_db((3232323323, 'ЛОХ', 'ЛОХОВИЧ'))
check_db()
