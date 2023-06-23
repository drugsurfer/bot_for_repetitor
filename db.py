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
            id_primary          INTEGER PRIMARY KEY,
            id     INTEGER NOT NULL,
            name   TEXT NOT NULL,
            sur_name TEXT NOT NULL);
    ''')

    connection.commit()

def init_students_db(force: bool = False):
    '''
    инициализирует базу учеников. force может перезаписать старую
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
            lesson_cost INTEGER NOT NULL);
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
        print(user[0], 'Уже есть в таблице users') # такой user_id уже есть в БД
    else:
        # такого user_id нет в БД
        c.execute('INSERT INTO user_data (id, name, sur_name) VALUES (?, ?, ?);', (user[0], user[1], user[2]))
    connection.commit()

def search_students_in_db(user_id: int, student_name: str, student_science: str):
    '''
    Ищет ученика по определенному критерию
    user_id - id преподавателя, среди учеников которого происходит поиск
    student_name - имя ученика
    student_science - предмет, которым занимается ученик
    '''
    connection = get_connection()
    c = connection.cursor()
    return c.execute('SELECT * FROM students WHERE id = ? AND name = ? AND science_object = ?', (user_id, student_name, student_science)).fetchall()

def add_student_to_db(student: tuple):
    '''
    Добавляет ученика в students.
    student = (user_id: int, name: str, sur_name: str, science_object: str, lesson_cost: int)
    '''
    user_id, name, sur_name, science_object, lesson_cost = student
    connection = get_connection()
    c = connection.cursor()
    if check_id_in_db(user_id, 'user_data'):
        # преподаватель ученика есть в базе
        if len(search_students_in_db(user_id, name, science_object)) == 0:
            c.execute('INSERT INTO students (id, name, sur_name, science_object, lesson_cost) VALUES (?, ?, ?, ?, ?);',
            (user_id, name, sur_name, science_object, lesson_cost))
        else:
            print(name, 'уже есть в таблице students')
    else:
        # ну каким-то волшебным образом не будет преподавателя в базе
        pass
    connection.commit()

def check_id_in_db(id: int, db_name: str):
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
    c.execute('SELECT * FROM students;')
    print(c.fetchall())

    
init_user_db()
init_students_db()
check_db()
add_user_to_db((1001, 'Евгений', 'Кондратьев'))
add_student_to_db((1001, 'Мария', 'Иванова', 'Физика', 700))
replace_value('Кондратьев', 'sur_name', 'user_data', 1)
check_db()
