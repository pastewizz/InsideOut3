import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def check_key():
    api_key = os.environ.get('GOOGLE_API_KEY')
    print(f"Checking Key: {api_key[:5]}...{api_key[-4:] if api_key else 'None'}")
    
    if not api_key:
        print("FAIL: No API Key found.")
        return

    client = genai.Client(api_key=api_key)
    
    try:
        print("Attempting to generate content with 'gemini-1.5-flash'...")
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Test.'
        )
        print("SUCCESS: API Key is valid and working.")
        print(f"Response: {response.text}")
    except Exception as e:
        print("\nERROR DETAILS:")
        print(f"{type(e).__name__}: {e}")
        
        err_str = str(e)
        if "400" in err_str and "API_KEY_INVALID" in err_str:
             print("\nDIAGNOSIS: The API Key is invalid.")
        elif "403" in err_str:
             print("\nDIAGNOSIS: The API Key may lack permissions or be expired (Quota/Billing).")
        elif "429" in err_str:
             print("\nDIAGNOSIS: Quota exhausted (Rate Limit).")

if __name__ == "__main__":
    check_key()
