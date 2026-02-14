import sqlite3
import os

def migrate():
    db_path = 'insideout.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. No migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add user_id to messages
    try:
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN user_id TEXT")
            print("Added user_id column to messages table.")
        else:
            print("user_id column already exists in messages table.")
    except Exception as e:
        print(f"Error migrating messages table: {e}")

    # 2. Update patterns user_id type (SQLite handles this via dynamic typing, but we ensure it works)
    # We don't strictly need to alter the column type in SQLite as it's manifest typing.
    # Existing data with user_id=1 will still work with our logic.

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
