import sqlite3


def create_or_clear_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        cursor.execute("DROP TABLE users")
    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, id_vk INTEGER, user_url TEXT, first_name TEXT, last_name TEXT, bdate TEXT, city TEXT, photo_urls TEXT)")
    conn.close()


def add_user_to_table(id_vk, user_url, first_name, last_name, bdate, city, photo=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if photo is not None:
        cursor.execute("INSERT INTO users (id_vk, user_url, first_name, last_name, bdate, city, photo_urls) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (id_vk, user_url, first_name, last_name, bdate, city, ','.join(photo)))
    else:
        cursor.execute("INSERT INTO users (id_vk, user_url, first_name, last_name, bdate, city) VALUES (?, ?, ?, ?, ?, ?)",
                       (id_vk, user_url, first_name, last_name, bdate, city))
    conn.commit()
    conn.close()