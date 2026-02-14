from dotenv import load_dotenv
load_dotenv()

from app import create_app
import os

# Mock the environment if needed, but run.py does load_dotenv. 
# We need to make sure load_dotenv is called or we manually load it for this test if create_app doesn't.
# app/__init__.py imports config, config imports os. 
# run.py is the one calling load_dotenv().

app = create_app()
key = app.config.get("GOOGLE_API_KEY")
print(f"Key in app config: {key}")

if key and key.startswith("AIza"):
    print("SUCCESS: Key correctly loaded into App Config.")
else:
    print("FAILURE: Key not found or invalid in App Config.")
