from app.db import save_message, get_recent_history, add_pattern, get_patterns, save_learning_topic, get_learning_topic, update_pattern_status
from app.ai_service import GeminiService

class ReflectionService:
    @staticmethod
    def get_reflection_response(user_id, feeling_text):
        """
        Generates a reflection response using Gemini.
        Orchestrates DB saving and AI generation.
        """
        # 1. Save User Message
        save_message(user_id=user_id, role='user', content=feeling_text)

        # 2. Get Context (History)
        history = get_recent_history(user_id=user_id, limit=8) 

        # 3. Generate Response (AI) - Returns dict: {reflection, insight, follow_up}
        ai_data = GeminiService.generate_response(feeling_text, history)
        
        if not ai_data:
            return {
                "error": "AI service unavailable",
                "message": "I'm having trouble connecting to my thought process right now. Please check the API key configuration."
            }

        reflection = ai_data.get("reflection", "")
        insight = ai_data.get("insight", "")
        follow_up = ai_data.get("follow_up", "")

        # 4. Save AI Response (Combine for DB history to keep context clean)
        combined_text = reflection
        if insight: combined_text += f"\n\n{insight}"
        if follow_up: combined_text += f"\n\n{follow_up}"
        
        save_message(user_id=user_id, role='ai', content=combined_text)
        
        # 5. Pattern Detection (Secondary Check)
        existing_patterns = get_patterns(user_id=user_id)
        patterns_summary = [f"{p['pattern_name']} ({p['status']})" for p in existing_patterns]
        
        analysis = GeminiService.analyze_patterns(feeling_text, history, patterns_summary)
        
        new_pattern_data = None
        if analysis and "patterns_detected" in analysis:
            for p in analysis["patterns_detected"]:
                pid, is_new = add_pattern(
                    pattern_name=p["name"],
                    pattern_type=p["type"],
                    confidence_score=p.get("confidence", 0),
                    weight=p.get("weight", 0),
                    user_id=user_id
                )
                
                if is_new and p.get("confidence", 0) >= 0.7 and p.get("weight", 0) >= 0.7:
                    topic = GeminiService.generate_learning_topic(p["name"], p["type"])
                    if topic:
                        save_learning_topic(
                            user_id=user_id,
                            pattern_id=pid,
                            topic_title=topic["title"],
                            topic_content=topic["content"],
                            interactive_hint=topic.get("interactive_hint")
                        )
                    
                    new_pattern_data = {
                        "id": pid,
                        "name": p["name"],
                        "type": p["type"]
                    }
                    break 

        # 6. Return formatted structure for UI pacing
        return {
            "type": "reflection",
            "message": reflection,
            "suggestion": insight if insight else None, 
            "follow_up": follow_up if follow_up else None,
            "new_pattern": new_pattern_data
        }

class DiscoveryService:
    @staticmethod
    def get_user_discoveries(user_id):
        """Fetches all patterns and their learning topics."""
        patterns = get_patterns(user_id=user_id)
        results = []
        for p in patterns:
            topic = get_learning_topic(user_id=user_id, pattern_id=p['id'])
            results.append({
                "pattern": p,
                "topic": topic
            })
        return results

    @staticmethod
    def acknowledge_pattern(user_id, pattern_id, status):
        update_pattern_status(user_id, pattern_id, status)
        return True

class ContentService:
    TOPICS = {
        "childhood": {
            "title": "Childhood & Emotional Patterns",
            "explanation": "Our early years often write the 'scripts' for how we handle emotions today.",
            "example": "If you had to hide sadness to be 'good', you might feel guilty when you're sad now.",
            "reflection_question": "What is one rule about feelings you learned as a child that might not serve you anymore?",
            "action": "Next time you feel an 'off-limits' emotion, tell yourself: 'I am safe to feel this.'"
        },
        "habits": {
            "title": "Habit Formation & Brain Wiring",
            "explanation": "Our brains love efficiency. They wire together thoughts and actions that we repeat often.",
            "example": "Doom-scrolling when xxious is a habit loop: Trigger (Anxiety) -> Action (Scroll) -> Reward (Distraction).",
            "reflection_question": "What is one small loop you find yourself stuck in when you are stressed?",
            "action": "Disrupt the loop gently. When you feel the urge, take just one deep breath before acting."
        },
        "confidence": {
            "title": "Confidence & Identity",
            "explanation": "Confidence isn't the absence of fear; it's the willingness to be yourself despite the fear.",
            "example": "You don't need to feel confident to take action. Action often creates confidence.",
            "reflection_question": "Where are you waiting to feel 'ready' before you start?",
            "action": "Do one tiny thing today that aligns with the person you want to be, even if your hands are shaking."
        },
        "regulation": {
            "title": "Emotional Regulation",
            "explanation": "Regulation isn't about suppressing feelings. It's about riding the wave without drowning.",
            "example": "Noticing 'I am feeling anger' instead of 'I am angry' creates a tiny bit of space.",
            "reflection_question": "What physical sensation tells you that you are starting to feel overwhelmed?",
            "action": "Practice 'grounding': name 3 things you can see, 2 you can touch, and 1 you can hear."
        }
    }

    @staticmethod
    def get_all_topics():
        return {k: v["title"] for k, v in ContentService.TOPICS.items()}

    @staticmethod
    def get_topic_content(topic_slug):
        return ContentService.TOPICS.get(topic_slug)

class LearningHubService:
    pass
