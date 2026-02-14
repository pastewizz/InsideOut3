from app import create_app
from app.db import init_db

# Create app and initialize database manually
app = create_app()
print("Manually initializing database...")
init_db(app)
print("Done! Checking tables...")

import sqlite3
conn = sqlite3.connect('insideout.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables created:")
for table in tables:
    print(f"  - {table[0]}")
conn.close()
