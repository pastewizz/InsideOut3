import sqlite3
import os
from flask import current_app, g

def get_db():
    """Connects to the database and ensures it is closed after the request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Initializes the database schema."""
    with app.app_context():
        db = get_db()
        # Create Messages Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT, -- For anonymous session isolation
                role TEXT NOT NULL, -- 'user' or 'ai'
                content TEXT NOT NULL,
                context_type TEXT,  -- e.g., 'feeling_checkup', 'general_chat'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create Patterns Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL, 
                pattern_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL, -- 'emotional', 'cognitive', 'behavioral'
                confidence_score REAL,
                weight REAL DEFAULT 0.0, -- Impact/Significance score (0-1)
                occurrences_count INTEGER DEFAULT 1,
                first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new' -- 'new', 'acknowledged', 'working_on_it', 'explored'
            )
        ''')
        # Create Learning Topics Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS learning_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                pattern_id INTEGER,
                topic_title TEXT NOT NULL,
                topic_content TEXT NOT NULL,
                interactive_hint TEXT,
                completion_status TEXT DEFAULT 'unread', -- 'unread', 'in_progress', 'completed'
                difficulty_level TEXT DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                FOREIGN KEY(pattern_id) REFERENCES patterns(id)
            )
        ''')
        # Create User Activity Table (Optional extension)
        db.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,
                detail TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

def save_message(user_id, role, content, context_type='general'):
    """Saves a message to the database."""
    db = get_db()
    db.execute(
        'INSERT INTO messages (user_id, role, content, context_type) VALUES (?, ?, ?, ?)',
        (user_id, role, content, context_type)
    )
    db.commit()

def get_recent_history(user_id, limit=10):
    """Retrieves the most recent chat messages for a user."""
    db = get_db()
    cursor = db.execute(
        'SELECT role, content FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?',
        (user_id, limit)
    )
    rows = cursor.fetchall()
    # Reverse to return chronologically (Oldest -> Newest)
    return [dict(row) for row in reversed(rows)]

# --- Pattern Helper Functions ---

def add_pattern(pattern_name, pattern_type, confidence_score, weight=0.0, user_id=None):
    """Adds a new pattern or updates an equivalent existing one."""
    db = get_db()
    
    # Check if a similar pattern applies (simple name check for now)
    cursor = db.execute(
        'SELECT id, occurrences_count FROM patterns WHERE pattern_name = ? AND user_id = ?',
        (pattern_name, user_id)
    )
    existing = cursor.fetchone()
    
    if existing:
        new_count = existing['occurrences_count'] + 1
        db.execute(
            '''UPDATE patterns 
               SET occurrences_count = ?, last_detected = CURRENT_TIMESTAMP, confidence_score = ?, weight = ?
               WHERE id = ?''',
            (new_count, confidence_score, weight, existing['id'])
        )
        db.commit()
        return existing['id'], False # False = not new
    else:
        cursor = db.execute(
            '''INSERT INTO patterns (user_id, pattern_name, pattern_type, confidence_score, weight) 
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, pattern_name, pattern_type, confidence_score, weight)
        )
        db.commit()
        return cursor.lastrowid, True # True = new

def get_patterns(user_id, filter_type=None):
    """Retrieves patterns for a user."""
    db = get_db()
    query = 'SELECT * FROM patterns WHERE user_id = ?'
    params = [user_id]
    
    if filter_type:
        query += ' AND pattern_type = ?'
        params.append(filter_type)
        
    query += ' ORDER BY last_detected DESC'
    
    cursor = db.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def update_pattern_status(user_id, pattern_id, status):
    """Updates the status of a pattern."""
    db = get_db()
    db.execute(
        'UPDATE patterns SET status = ? WHERE id = ? AND user_id = ?',
        (status, pattern_id, user_id)
    )
    db.commit()

def save_learning_topic(user_id, pattern_id, topic_title, topic_content, interactive_hint, difficulty='beginner'):
    """Saves an AI-generated learning topic."""
    db = get_db()
    db.execute(
        '''INSERT INTO learning_topics (user_id, pattern_id, topic_title, topic_content, interactive_hint, difficulty_level)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, pattern_id, topic_title, topic_content, interactive_hint, difficulty)
    )
    db.commit()

def get_learning_topic(user_id, pattern_id):
    """Retrieves the learning topic for a pattern."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM learning_topics WHERE pattern_id = ? AND user_id = ?',
        (pattern_id, user_id)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def get_all_learning_topics(user_id):
    """Retrieves all learning topics for a user."""
    db = get_db()
    cursor = db.execute(
        '''SELECT t.*, p.pattern_name, p.pattern_type 
           FROM learning_topics t 
           JOIN patterns p ON t.pattern_id = p.id 
           WHERE t.user_id = ?
           ORDER BY t.created_at DESC''',
        (user_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def update_topic_progress(user_id, topic_id, status):
    """Updates the completion status of a topic."""
    db = get_db()
    db.execute(
        'UPDATE learning_topics SET completion_status = ?, last_accessed = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
        (status, topic_id, user_id)
    )
    db.commit()

