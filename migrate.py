import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

if not os.path.exists(db_path):
    print("No database found.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ['plan', 'member', 'attendance', 'payment', 'expense', 'enquiry', 'visitor', 'reminder']

try:
    cursor.execute("SELECT id FROM staff LIMIT 1")
    user = cursor.fetchone()
    user_id = user[0] if user else 1
except Exception as e:
    user_id = 1

for table in tables:
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER REFERENCES staff(id)")
        cursor.execute(f"UPDATE {table} SET user_id = ?", (user_id,))
        print(f"Migrated {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column already exists for {table}")
        else:
            print(f"Error migrating {table}: {e}")

conn.commit()
conn.close()
