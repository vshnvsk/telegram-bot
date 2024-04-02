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
    cursor.execute(f"SELECT DISTINCT name FROM Ordinary_Subjects WHERE group_{group} = 1 ORDER BY name")
    data = cursor.fetchall()
    return data


def get_selected_subject(subject):
    cursor.execute(f"SELECT DISTINCT name FROM Elective_Subjects WHERE abbreviation = '{subject}' ORDER BY name")
    data = cursor.fetchall()
    return data
