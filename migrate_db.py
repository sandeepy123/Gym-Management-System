import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE attendance ADD COLUMN exit_time TIME')
    print("Successfully added exit_time to attendance table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column exit_time already exists.")
    else:
        print(f"Error: {e}")

try:
    cursor.execute('''
        CREATE TABLE reminder (
            id INTEGER PRIMARY KEY,
            member_id INTEGER NOT NULL,
            date_sent DATE NOT NULL,
            type VARCHAR(64) NOT NULL,
            FOREIGN KEY(member_id) REFERENCES member(id)
        )
    ''')
    print("Successfully created reminder table.")
except sqlite3.OperationalError as e:
    if "already exists" in str(e):
        print("Table reminder already exists.")
    else:
        print(f"Error: {e}")

conn.commit()
conn.close()
