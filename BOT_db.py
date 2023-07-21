import sqlite3
from BOT_const import *


# conn = sqlite3.connect(path)
# cursor = conn.cursor()
# cursor.execute("""CREATE TABLE IF NOT EXISTS users(
#    userid,
#    link);
# """)
# conn.commit()
# cursor.close()
# conn.close()


def add_new_string(id, url):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = (id, url)
    sql = "INSERT INTO users VALUES (?, ?)"
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()


def check_if_in(id, url):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    link = url
    val = (id, link)
    cursor.execute('select count(*) from users where userid = ? and link = ?', (val))
    for i in cursor:
        k = i[0]
    cursor.close()
    conn.close()
    return k


def check_if_user(id):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = id
    cursor.execute('select count(*) from users where userid = ? ', (val,))
    for i in cursor:
        k = i[0]
    cursor.close()
    conn.close()
    return k


def delete_user(id):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    val = id
    cursor.execute("DELETE FROM users WHERE userid=?", (val,))
    conn.commit()
    cursor.close()
    conn.close()