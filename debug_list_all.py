import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_gen_models():
    api_key = os.environ.get('GOOGLE_API_KEY')
    client = genai.Client(api_key=api_key)
    try:
        print("Listing generateContent models...")
        for m in client.models.list():
            if m.supported_actions and 'generateContent' in m.supported_actions:
                print(f"FOUND: {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_gen_models()
