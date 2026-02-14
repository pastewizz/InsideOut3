import os
import sqlite3
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, g

# Import app modules
from app.db import init_db, get_db, get_patterns
from app.services import ReflectionService
from app.ai_service import GeminiService

class TestPatternRefinement(unittest.TestCase):
    def setUp(self):
        self.db_path = f'test_refinement_{os.urandom(4).hex()}.db'
        self.app = Flask(__name__)
        self.app.config['DATABASE_PATH'] = self.db_path
        self.app.config['GOOGLE_API_KEY'] = 'fake_key'
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

    def tearDown(self):
        self.app_context.pop()
        # Clean up db file
        try:
            if os.path.exists(self.db_path):
                # Close any lingering connections? Python's garbage collection should handle it if context popped
                # But let's force a small wait or just ignore if locked for now (it's a temp file, OS will clean eventually or we ignore)
                os.remove(self.db_path)
        except PermissionError:
            pass

    @patch('app.ai_service.GeminiService.generate_response')
    @patch('app.ai_service.GeminiService.analyze_patterns')
    @patch('app.ai_service.GeminiService.generate_learning_topic')
    def test_trivial_pattern_ignored(self, mock_learning, mock_analyze, mock_generate):
        print("\n--- Testing Trivial Pattern (Should be Ignored) ---")
        mock_generate.return_value = "Basic response."
        
        # Mock analysis returning a low-weight pattern
        mock_analyze.return_value = {
            "patterns_detected": [
                {
                    "name": "Direct Communication",
                    "type": "behavioral",
                    "confidence": 0.9,
                    "weight": 0.2, # LOW WEIGHT
                    "is_new": True,
                    "reasoning": "User speaks directly."
                }
            ]
        }
        
        response = ReflectionService.get_reflection_response("I told him directly what I thought.")
        
        # Should NOT trigger notification
        self.assertIsNone(response.get('new_pattern'))
        
        # But SHOULD be saved to DB for analytics
        patterns = get_patterns(user_id=1)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]['pattern_name'], "Direct Communication")
        print("SUCCESS: Trivial pattern was saved for analytics but NOT notified.")

    @patch('app.ai_service.GeminiService.generate_response')
    @patch('app.ai_service.GeminiService.analyze_patterns')
    @patch('app.ai_service.GeminiService.generate_learning_topic')
    def test_meaningful_pattern_accepted(self, mock_learning, mock_analyze, mock_generate):
        print("\n--- Testing Meaningful Pattern (Should be Accepted) ---")
        mock_generate.return_value = "Response."
        mock_learning.return_value = {"title": "T", "content": "C", "interactive_hint": "H"}
        
        # Mock analysis returning a high-weight pattern
        mock_analyze.return_value = {
            "patterns_detected": [
                {
                    "name": "Avoidance Coping",
                    "type": "behavioral",
                    "confidence": 0.8,
                    "weight": 0.9, # HIGH WEIGHT
                    "is_new": True,
                    "reasoning": "User avoids conflict repeatedly."
                }
            ]
        }
        
        response = ReflectionService.get_reflection_response("I avoided him again.")
        
        self.assertIsNotNone(response.get('new_pattern'))
        print(f"Detected: {response['new_pattern']['name']}")
        
        patterns = get_patterns(user_id=1)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]['pattern_name'], "Avoidance Coping")
        print("SUCCESS: Meaningful pattern was saved and notified.")

if __name__ == '__main__':
    unittest.main()
