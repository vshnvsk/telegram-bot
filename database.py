import sqlite3

global db, cursor

db = sqlite3.connect("schedule.db")

cursor = db.cursor()


async def db_connect() -> None:
    global db, cursor

    db = sqlite3.connect("schedule.db")
    cursor = db.cursor()


def get_ordinary_subject(group):
    cursor.execute(f"SELECT DISTINCT name FROM Ordinary_Subjects "
                   f"WHERE group_{group} = 1 ORDER BY name")
    data = cursor.fetchall()
    return data


def get_selected_subject(subject):
    cursor.execute(f"SELECT DISTINCT name FROM Elective_Subjects "
                   f"WHERE abbreviation = '{subject}' ORDER BY name")
    data = cursor.fetchall()
    return data


def get_all_subject_first_week(user_group, user_select):
    values = ['"' + item['name'] + '"' for user_id, selected_subjects in user_select.items() for item in
              selected_subjects]

    values_str = ', '.join(values)

    cursor.execute("""
        SELECT 
            weekday, 
            id_call, 
            name, 
            academic_status, 
            teacher_name, 
            lesson_type, 
            number_of_audience, 
            start, 
            end, 
            type_of_closure 
        FROM (
            SELECT 
                Ordinary_Subjects.weekday, 
                Ordinary_Subjects.id_call, 
                Ordinary_Subjects.name, 
                Teacher.academic_status, 
                Teacher.name AS teacher_name,
                Ordinary_Subjects.lesson_type, 
                Ordinary_Subjects.number_of_audience,  
                Call_Schedule.start, 
                Call_Schedule.end,
                Ordinary_Subjects.type_of_closure,
                CASE 
                    WHEN Ordinary_Subjects.weekday = 'Понеділок' THEN 1 
                    WHEN Ordinary_Subjects.weekday = 'Вівторок' THEN 2 
                    WHEN Ordinary_Subjects.weekday = 'Середа' THEN 3 
                    WHEN Ordinary_Subjects.weekday = 'Четвер' THEN 4 
                    WHEN Ordinary_Subjects.weekday = 'П''ятниця' THEN 5 
                END AS day_order 
            FROM 
                Ordinary_Subjects 
            JOIN 
                Teacher ON Teacher.id_teacher = Ordinary_Subjects.id_teacher 
            JOIN 
                Call_Schedule ON Call_Schedule.id_call = Ordinary_Subjects.id_call 
            WHERE 
                Ordinary_Subjects.group_{} = 1 
                AND (
                    Ordinary_Subjects.number_of_audience <> '8-213' 
                    OR Ordinary_Subjects.name != 'Моделювання систем'
                ) 
                AND (
                    Ordinary_Subjects.id_call <> 3 
                    OR Ordinary_Subjects.name != 'Крос-платформне програмування'
                ) 
            UNION ALL 
            SELECT 
                Elective_Subjects.weekday, 
                Elective_Subjects.id_call,
                Elective_Subjects.name, 
                Teacher.academic_status, 
                Teacher.name AS teacher_name,
                Elective_Subjects.lesson_type, 
                Elective_Subjects.number_of_audience, 
                Call_Schedule.start, 
                Call_Schedule.end,
                Elective_Subjects.type_of_closure,
                CASE 
                    WHEN Elective_Subjects.weekday = 'Понеділок' THEN 1 
                    WHEN Elective_Subjects.weekday = 'Вівторок' THEN 2 
                    WHEN Elective_Subjects.weekday = 'Середа' THEN 3 
                    WHEN Elective_Subjects.weekday = 'Четвер' THEN 4 
                    WHEN Elective_Subjects.weekday = 'П''ятниця' THEN 5 
                END AS day_order 
            FROM 
                Elective_Subjects 
            JOIN 
                Teacher ON Teacher.id_teacher = Elective_Subjects.id_teacher 
            JOIN 
                Call_Schedule ON Call_Schedule.id_call = Elective_Subjects.id_call 
            WHERE 
                abbreviation IN ({}) 
                AND Elective_Subjects.group_{} = 1 
                AND (
                    Elective_Subjects.id_call <> 4 
                    OR Elective_Subjects.name != 'Програмування мобільних додатків'
                ) 
                AND (
                    Elective_Subjects.number_of_audience <> '8-117' 
                    OR Elective_Subjects.name != 'Теорія інформації та кодування'
                ) 
        ) AS sub 
        ORDER BY 
            day_order, id_call
    """.format(user_group, ','.join('?' * len(values)), user_group), values)

    data = cursor.fetchall()
    return data


def get_all_subject_second_week(user_group, user_select):
    cursor.execute(f"SELECT "
                   f"sub.weekday, "
                   f"sub.id_call, "
                   f"sub.name, "
                   f"sub.academic_status, "
                   f"sub.teacher_name, "
                   f"sub.lesson_type, "
                   f"sub.number_of_audience, "
                   f"sub.start, "
                   f"sub.end, "
                   f"sub.type_of_closure "
                   f"FROM ( SELECT "
                   f"Ordinary_Subjects.weekday, "
                   f"Ordinary_Subjects.id_call, "
                   f"Ordinary_Subjects.name, "
                   f"Teacher.academic_status, "
                   f"Teacher.name AS teacher_name,"
                   f"Ordinary_Subjects.lesson_type, "
                   f"Ordinary_Subjects.number_of_audience,  "
                   f"Call_Schedule.start, "
                   f"Call_Schedule.end, "
                   f"Ordinary_Subjects.type_of_closure, "
                   f"CASE "
                   f"WHEN Ordinary_Subjects.weekday = 'Понеділок' THEN 1 "
                   f"WHEN Ordinary_Subjects.weekday = 'Вівторок' THEN 2 "
                   f"WHEN Ordinary_Subjects.weekday = 'Середа' THEN 3 "
                   f"WHEN Ordinary_Subjects.weekday = 'Четвер' THEN 4 "
                   f"WHEN Ordinary_Subjects.weekday = 'П''ятниця' THEN 5 "
                   f"END AS day_order "
                   f"FROM Ordinary_Subjects "
                   f"JOIN "
                   f"Teacher ON Teacher.id_teacher = Ordinary_Subjects.id_teacher "
                   f"JOIN "
                   f"Call_Schedule ON Call_Schedule.id_call = Ordinary_Subjects.id_call "
                   f"WHERE "
                   f"Ordinary_Subjects.group_{user_group} = 1 "
                   f"AND (Ordinary_Subjects.number_of_audience <> '8-212' "
                   f"OR Ordinary_Subjects.name != 'Моделювання систем') "
                   f"AND (Ordinary_Subjects.id_call <> 1 "
                   f"OR Ordinary_Subjects.weekday != 'Четвер' "
                   f"OR Ordinary_Subjects.name != 'Крос-платформне програмування') "
                   f"UNION ALL "
                   f"SELECT "
                   f"Elective_Subjects.weekday, "
                   f"Elective_Subjects.id_call,"
                   f"Elective_Subjects.name, "
                   f"Teacher.academic_status, "
                   f"Teacher.name AS teacher_name,"
                   f"Elective_Subjects.lesson_type, "
                   f"Elective_Subjects.number_of_audience, "
                   f"Call_Schedule.start, "
                   f"Call_Schedule.end, "
                   f"Elective_Subjects.type_of_closure, "
                   f"CASE "
                   f"WHEN Elective_Subjects.weekday = 'Понеділок' THEN 1 "
                   f"WHEN Elective_Subjects.weekday = 'Вівторок' THEN 2 "
                   f"WHEN Elective_Subjects.weekday = 'Середа' THEN 3 "
                   f"WHEN Elective_Subjects.weekday = 'Четвер' THEN 4 "
                   f"WHEN Elective_Subjects.weekday = 'П''ятниця' THEN 5 "
                   f"END AS day_order "
                   f"FROM Elective_Subjects "
                   f"JOIN "
                   f"Teacher ON Teacher.id_teacher = Elective_Subjects.id_teacher "
                   f"JOIN "
                   f"Call_Schedule ON Call_Schedule.id_call = Elective_Subjects.id_call "
                   f"WHERE "
                   f"abbreviation IN {user_select}"
                   f"AND Elective_Subjects.group_{user_group} = 1 "
                   f"AND (Elective_Subjects.number_of_audience <> '8-325' "
                   f"OR Elective_Subjects.name != 'Теорія інформації та кодування') "
                   f") AS sub "
                   f"ORDER BY "
                   f"sub.day_order, sub.id_call")

    data = cursor.fetchall()
    return data