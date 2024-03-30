import sqlite3

async def db_connect() -> None:

    global db, cursor

    db = sqlite3.connect("schedule.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()


def get_ordinary_subject(group):
    cursor.execute(f"SELECT DISTINCT name FROM Ordinary_Subject WHERE group_{group} = 1 ORDER BY name")
    data = cursor.fetchall()
    return data
