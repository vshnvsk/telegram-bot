import sqlite3

global db, cursor

db = sqlite3.connect("schedule.db")

cursor = db.cursor()


async def db_connect() -> None:
    global db, cursor

    db = sqlite3.connect("schedule.db")
    #db.row_factory = sqlite3.Row
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


def get_all_subject(group):
    cursor.execute(f"SELECT weekday, "
                        f"id_call, "
                        f"name, "
                        f"academic_status, "
                        f"teacher_name, "
                        f"lesson_type, "
                        f"number_of_audience, "
                        f"start, "
                        f"end, "
                        f"type_of_closure "
                   f"FROM "
                   f"( SELECT "
                        f"Ordinary_Subjects.weekday, "
                        f"Ordinary_Subjects.id_call, "
                        f"Ordinary_Subjects.name, "
                        f"Teacher.academic_status, "
                        f"Teacher.name AS teacher_name,"
                        f"Ordinary_Subjects.lesson_type, "
                        f"Ordinary_Subjects.number_of_audience,  "
                        f"Call_Schedule.start, "
                        f"Call_Schedule.end,"
                        f"Ordinary_Subjects.type_of_closure,"
                   f"CASE "
                        f"WHEN Ordinary_Subjects.weekday = 'Понеділок' THEN 1"
                        f"WHEN Ordinary_Subjects.weekday = 'Вівторок' THEN 2"
                        f"WHEN Ordinary_Subjects.weekday = 'Середа' THEN 3"
                        f"WHEN Ordinary_Subjects.weekday = 'Четвер' THEN 4"
                        f"WHEN Ordinary_Subjects.weekday = 'П\'ятниця' THEN 5"
                   f"END AS day_order)"
                   f"FROM "
                        f"Ordinary_Subjects"
                   f"JOIN "
                        f"Teacher ON Teacher.id_teacher = Ordinary_Subjects.id_teacher"
                   f"JOIN "
                        f"Call_Schedule ON Call_Schedule.id_call = Ordinary_Subjects.id_call"
                   f"WHERE "
                        f"Ordinary_Subjects.group_{group} = 1"
                   f"UNION ALL"
                   f"SELECT "
                        f"Elective_Subjects.weekday, "
                        f"Elective_Subjects.id_call,"
                        f"Elective_Subjects.name, "
                        f"Teacher.academic_status, "
                        f"Teacher.name AS teacher_name,"
                        f"Elective_Subjects.lesson_type, "
                        f"Elective_Subjects.number_of_audience, "
                        f"Call_Schedule.start, "
                        f"Call_Schedule.end,"
                        f"Elective_Subjects.type_of_closure,"
                   f"CASE "
                        f"WHEN Elective_Subjects.weekday = 'Понеділок' THEN 1"
                        f"WHEN Elective_Subjects.weekday = 'Вівторок' THEN 2"
                        f"WHEN Elective_Subjects.weekday = 'Середа' THEN 3"
                        f"WHEN Elective_Subjects.weekday = 'Четвер' THEN 4"
                        f"WHEN Elective_Subjects.weekday = 'П\'ятниця' THEN 5"
                   f"END AS day_order"
                   f"FROM "
                        f"Elective_Subjects"
                   f"JOIN "
                        f"Teacher ON Teacher.id_teacher = Elective_Subjects.id_teacher"
                   f"JOIN "
                        f"Call_Schedule ON Call_Schedule.id_call = Elective_Subjects.id_call"
                   f"WHERE "
                        f"abbreviation IN ('mobileapps', 'internet', 'ruby')" # ще тут треба
                   f") AS sub"
                   f"ORDER BY "
                        f"day_order")