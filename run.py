from dotenv import load_dotenv
load_dotenv()
from app import create_app
import os
import sys

# Simple startup check
def check_startup():
    print("Checking startup requirements...")
    if not os.environ.get("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY is not set. AI features will not work.")
        print("Please check your .env file.")
    else:
        print("KEY FOUND: GOOGLE_API_KEY detected.")

check_startup()

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
