# setup_db.py
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Tambahkan user admin awal (opsional)
hashed_pw = generate_password_hash("admin123")
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", hashed_pw))

conn.commit()
conn.close()
print("Database selesai dibuat.")
