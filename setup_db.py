# setup_db.py versi MySQL
import pymysql
from werkzeug.security import generate_password_hash

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='ocr_v3'
)

with connection.cursor() as cursor:
    sql = """
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255) UNIQUE NOT NULL,
      password VARCHAR(255) NOT NULL
    )
    """
    cursor.execute(sql)

    hashed_pw = generate_password_hash("admin123")
    cursor.execute("INSERT IGNORE INTO users (username, password) VALUES (%s, %s)", ("admin", hashed_pw))

    connection.commit()

print("Database MySQL selesai dibuat.")
