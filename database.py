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


def get_all_subject_first_week(user_group, user_select, weekday):
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
                   f"AND Ordinary_Subjects.weekday = '{weekday}' "
                   f"AND (Ordinary_Subjects.number_of_audience <> '8-213' "
                   f"OR Ordinary_Subjects.name != 'Моделювання систем') "
                   f"AND (Ordinary_Subjects.id_call <> 3 "
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
                   f"AND Elective_Subjects.weekday = '{weekday}' "
                   f"AND (Elective_Subjects.id_call <> 4 "
                   f"OR Elective_Subjects.name != 'Програмування мобільних додатків') "
                   f"AND (Elective_Subjects.number_of_audience <> '8-117' "
                   f"OR Elective_Subjects.name != 'Теорія інформації та кодування') "  
                   f") AS sub "
                   f"ORDER BY "
                   f"sub.day_order, sub.id_call")

    data = cursor.fetchall()
    return data


def get_all_subject_second_week(user_group, user_select, weekday):
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
                   f"AND Ordinary_Subjects.weekday = '{weekday}' "
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
                   f"AND Elective_Subjects.weekday = '{weekday}' "
                   f"AND (Elective_Subjects.number_of_audience <> '8-325' "
                   f"OR Elective_Subjects.name != 'Теорія інформації та кодування') "
                   f") AS sub "
                   f"ORDER BY "
                   f"sub.day_order, sub.id_call")

    data = cursor.fetchall()
    return data


def get_links(user_group, user_select, type_of_link):
    cursor.execute(f"SELECT name, link, pass FROM Links "
                   f"WHERE group_{user_group} = 1 "
                   f"AND type_of_link = '{type_of_link}' "
                   f"AND abbreviation IS NULL "
                   f"OR (abbreviation IN {user_select} AND type_of_link = '{type_of_link}')")

    data = cursor.fetchall()
    return data