import os
from google import genai

client = genai.Client(api_key="AIzaSyAxvtJGHA6b2p5U7V4RothZj0V6GKUtrjM")

try:
    response = client.models.generate_content(
        model="gemini-pro-latest",
        contents="Say hello!"
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
 