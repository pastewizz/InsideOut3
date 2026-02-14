import os
import sys
import sqlite3
from pathlib import Path

# Colors for feedback
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(message, status="INFO"):
    if status == "OK":
        print(f"[{GREEN}OK{RESET}] {message}")
    elif status == "FAIL":
        print(f"[{RED}FAIL{RESET}] {message}")
    elif status == "WARN":
        print(f"[{YELLOW}WARN{RESET}] {message}")
    else:
        print(f"[INFO] {message}")

def check_env_file():
    env_path = Path('.env')
    if env_path.exists():
        print_status(".env file found", "OK")
        return True
    else:
        print_status(".env file missing", "WARN")
        return False

def check_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    key = os.environ.get('GOOGLE_API_KEY')
    if key:
        print_status(f"GOOGLE_API_KEY found (starts with {key[:4]}...)", "OK")
        return key
    else:
        print_status("GOOGLE_API_KEY not found in environment or .env", "FAIL")
        return None

def check_dependencies():
    try:
        import flask
        import google.genai
        from dotenv import load_dotenv
        print_status("Dependencies (Flask, google-genai, python-dotenv) installed", "OK")
        return True
    except ImportError as e:
        print_status(f"Missing dependency: {e}", "FAIL")
        return False

def check_database():
    db_path = Path('insideout.db')
    # It might not exist yet if app hasn't run, but we can check write permissions
    try:
        conn = sqlite3.connect('insideout.db')
        conn.close()
        print_status("Database connection successful (SQLite)", "OK")
        return True
    except Exception as e:
        print_status(f"Database check failed: {e}", "FAIL")
        return False

def check_api_connectivity(api_key):
    if not api_key:
        return False
    
    from google import genai
    print_status("Testing Gemini API connectivity...", "INFO")
    try:
        client = genai.Client(api_key=api_key)
        # Try a robust model first
        try:
            client.models.generate_content(model="gemini-1.5-flash", contents="Ping")
            print_status("API Connection successful (gemini-1.5-flash)", "OK")
            return True
        except Exception as e:
            print_status(f"Model 'gemini-1.5-flash' failed: {e}", "WARN")
            
            # Try verification with list models
            try:
                list(client.models.list(config={'page_size': 1}))
                print_status("API Key is valid (ListModels worked), but generation failed.", "WARN")
                return True
            except Exception as e2:
                print_status(f"API Key validation completely failed: {e2}", "FAIL")
                return False

    except Exception as e:
        print_status(f"Client instantiation failed: {e}", "FAIL")
        return False

def run_diagnostics():
    print("--- Starting System Diagnostics ---\n")
    
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\nPlease install missing dependencies: pip install -r requirements.txt")
        return
        
    env_exists = check_env_file()
    api_key = check_api_key()
    
    db_ok = check_database()
    
    api_ok = False
    if api_key:
        api_ok = check_api_connectivity(api_key)
    
    print("\n--- Diagnostic Summary ---")
    if deps_ok and api_key and db_ok and api_ok:
        print(f"{GREEN}All systems operational.{RESET} You can run the app.")
    else:
        print(f"{RED}Issues detected.{RESET} Please resolve the failures above.")

if __name__ == "__main__":
    run_diagnostics()
