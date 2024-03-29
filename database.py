import sqlite3


async def db_connect() -> None:

    db = sqlite3.connect("schedule.db")
    cursor = db.cursor()

    #
    # group_341A = cursor.execute("""SELECT DISTINCT name FROM Ordinary_Subject
    # WHERE group_341A = 1""")
    #
    # group_341B = cursor.execute("""SELECT DISTINCT name FROM Ordinary_Subject
    # WHERE group_341B = 1""")
    #
    # group_341Short = cursor.execute("""SELECT DISTINCT name FROM Ordinary_Subject
    # WHERE group_341Short = 1""")


    cursor.execute("""SELECT DISTINCT name FROM Ordinary_Subject WHERE group_341A = 1""").fetchall()

    cursor.close()
    db.close()
