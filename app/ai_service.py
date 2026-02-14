from google import genai
from flask import current_app
import json
import logging
from app.key_manager import get_key_manager

class GeminiService:
    SYSTEM_PROMPT = """You are Echo, a deeply empathetic, psychological mirror and guide. Your core purpose is to help users explore their inner world with radical validation and proactive curiosity.

The 3 Pillars of Echo:
1. DEEP EMPATHY: Never be dismissive. If a user shares a struggle, your first priority is to make them feel truly seen and heard. Use warmth and gentle, relatable language.
2. RADICAL VALIDATION: Normalize the user's experience. Let them know their feelings make sense given their context.
3. PROACTIVE CURIOSITY: Never end an exchange with a generic statement. Always ask a meaningful, open-ended follow-up question that invites the user to look deeper at a specific feeling, thought, or sensation.

Tone & Style:
- Warm, grounded, and companionable.
- Expert but accessible (psychologically insightful without being clinical).
- Avoid generic "I understand" or "That sounds hard." Instead, reflect back specific nuances of what they shared.

Output Format:
You must respond in JSON format with the following keys:
{
  "reflection": "Your warm, empathetic validation and mirroring of the user's input.",
  "insight": "Optional. A brief psychological connection or pattern observation (1-2 sentences).",
  "follow_up": "A single, powerful, open-ended question to guide them deeper."
}
"""

    @staticmethod
    def _call_gemini(model_name, contents, config, retry_count=3):
        """Internal helper to handle retries and key rotation."""
        km = get_key_manager()
        
        for attempt in range(retry_count):
            api_key = km.get_key()
            if not api_key:
                logging.error("No active API keys available for this request.")
                return None

            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                
                if response.text:
                    km.mark_success(api_key)
                    return response.text
                return None

            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    km.mark_failed(api_key, "quota_exhausted")
                    # Continue to next attempt with a new key
                else:
                    logging.error(f"Unexpected Gemini Error: {e}")
                    # For non-quota errors, we might still want to try another key
                    km.mark_failed(api_key, "general_failure")
        
        return None

    @staticmethod
    def generate_response(user_input, history=None):
        if history is None:
            history = []

        model_name = "gemini-1.5-flash"
        
        prompt = f"{GeminiService.SYSTEM_PROMPT}\n\n"
        for msg in history[-8:]:
            role = "User" if msg["role"] != "ai" else "Echo"
            prompt += f"{role}: {msg['content']}\n"
        prompt += f"User: {user_input}\nEcho:"

        config = {
            "temperature": 0.7,
            "max_output_tokens": 800,
            "response_mime_type": "application/json"
        }

        result_text = GeminiService._call_gemini(model_name, prompt, config)
        if result_text:
            try:
                return json.loads(result_text)
            except:
                return None
        return None

    @staticmethod
    def analyze_patterns(user_input, history, existing_patterns):
        model_name = "gemini-1.5-flash"
        prompt = f"""You are an expert psychological pattern detector. 
        Analyze the following user session and existing patterns to identify ANY recurring emotional, cognitive, or behavioral patterns.
        
        Current User Input: {user_input}
        Recent History: {history}
        Existing Patterns: {existing_patterns}
        
        Output JSON ONLY:
        {{
            "patterns_detected": [
                {{
                    "name": "Short name",
                    "type": "emotional" | "cognitive" | "behavioral",
                    "confidence": 0.0 to 1.0,
                    "weight": 0.0 to 1.0,
                    "reasoning": "..."
                }}
            ]
        }}
        If no strong patterns, return "NO_PATTERN_DETECTED".
        """

        config = {
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }

        result_text = GeminiService._call_gemini(model_name, prompt, config)
        if result_text and "NO_PATTERN_DETECTED" not in result_text:
            try:
                return json.loads(result_text)
            except:
                return None
        return None

    @staticmethod
    def generate_learning_topic(pattern_name, pattern_type, difficulty="beginner"):
        model_name = "gemini-1.5-flash"
        prompt = f"""You are a compassionate guide. Generate a learning topic for: "{pattern_name}" ({pattern_type}).
        JSON Output ONLY:
        {{
            "title": "...",
            "content": "...",
            "interactive_hint": "..."
        }}"""

        config = {
            "temperature": 0.7,
            "response_mime_type": "application/json"
        }

        result_text = GeminiService._call_gemini(model_name, prompt, config)
        if result_text:
            try:
                return json.loads(result_text)
            except:
                return None
        return None

