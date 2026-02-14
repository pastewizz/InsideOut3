import sqlite3
import os

for db_file in os.listdir('.'):
    if db_file.endswith('.db'):
        print(f"\n{db_file}:")
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM patterns')
            print(f"  Patterns: {c.fetchone()[0]}")
            c.execute('SELECT COUNT(*) FROM learning_topics')
            print(f"  Topics: {c.fetchone()[0]}")
            conn.close()
        except Exception as e:
            print(f"  Error: {e}")
