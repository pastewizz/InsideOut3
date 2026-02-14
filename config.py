import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-prod'
    
    # Support for multiple API keys
    GOOGLE_API_KEYS = [
        os.environ.get('GOOGLE_API_KEY'),
        os.environ.get('GOOGLE_API_KEY_2'),
        os.environ.get('GOOGLE_API_KEY_3'),
        os.environ.get('GOOGLE_API_KEY_4')
    ]
    # Filter out None values
    GOOGLE_API_KEYS = [k for k in GOOGLE_API_KEYS if k]
    
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'insideout_prod.db')
