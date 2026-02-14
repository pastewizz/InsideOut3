import sqlite3

# Check the schema
conn = sqlite3.connect('insideout.db')
cursor = conn.cursor()

# Get learning_topics table schema
cursor.execute("PRAGMA table_info(learning_topics)")
columns = cursor.fetchall()

print("learning_topics table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
