import sqlite3

DB_NAME = 'contact_book.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')
        con.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            linkedin TEXT,
            category TEXT
        )''')

class User:
    @staticmethod
    def register(username, password):
        try:
            with get_connection() as con:
                con.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def authenticate(username, password):
        with get_connection() as con:
            user = con.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            return bool(user)

    @staticmethod
    def get_by_username(username):
        with get_connection() as con:
            return con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

class Contact:
    @staticmethod
    def get_all(user_id, query=""):
        with get_connection() as con:
            if query:
                query = f"%{query}%"
                return con.execute('''
                    SELECT * FROM contacts
                    WHERE user_id=? AND (first_name LIKE ? OR last_name LIKE ?)
                    ORDER BY first_name ASC
                ''', (user_id, query, query)).fetchall()
            return con.execute("SELECT * FROM contacts WHERE user_id=? ORDER BY first_name ASC", (user_id,)).fetchall()

    @staticmethod
    def add(user_id, data):
        with get_connection() as con:
            con.execute('''
                INSERT INTO contacts (user_id, first_name, last_name, phone, email, address, linkedin, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data['first_name'],
                data['last_name'],
                data['phone'],
                data['email'],
                data['address'],
                data['linkedin'],
                data['category']
            ))

    @staticmethod
    def get_by_id(contact_id):
        with get_connection() as con:
            return con.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone()

    @staticmethod
    def update(contact_id, data):
        with get_connection() as con:
            con.execute('''
                UPDATE contacts
                SET first_name=?, last_name=?, phone=?, email=?, address=?, linkedin=?, category=?
                WHERE id=?
            ''', (
                data['first_name'],
                data['last_name'],
                data['phone'],
                data['email'],
                data['address'],
                data['linkedin'],
                data['category'],
                contact_id
            ))

    @staticmethod
    def delete(contact_id):
        with get_connection() as con:
            con.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
