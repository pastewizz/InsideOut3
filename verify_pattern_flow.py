import os
import sqlite3
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, g

# Import app modules - assuming we are in root
from app.db import init_db, get_db, get_patterns
from app.services import ReflectionService
from app.ai_service import GeminiService

class TestPatternFlow(unittest.TestCase):
    def setUp(self):
        # Setup temporary test app
        self.app = Flask(__name__)
        self.app.config['DATABASE_PATH'] = 'test_insideout.db'
        self.app.config['GOOGLE_API_KEY'] = 'fake_key' # We will mock the API calls
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize DB
        init_db(self.app)

    def tearDown(self):
        self.app_context.pop()
        # Clean up db file
        if os.path.exists('test_insideout.db'):
            os.remove('test_insideout.db')

    @patch('app.ai_service.GeminiService.generate_response')
    @patch('app.ai_service.GeminiService.analyze_patterns')
    @patch('app.ai_service.GeminiService.generate_learning_topic')
    def test_pattern_detection_flow(self, mock_learning, mock_analyze, mock_generate):
        # 1. Setup Mocks
        mock_generate.return_value = "I hear you. That sounds tough."
        
        # Mocking the analysis to return a specific new pattern
        mock_analyze.return_value = {
            "patterns_detected": [
                {
                    "name": "Test Pattern",
                    "type": "emotional",
                    "confidence": 0.8,
                    "is_new": True,
                    "reasoning": "Test reasoning"
                }
            ]
        }
        
        # Mocking learning topic generation
        mock_learning.return_value = {
            "title": "Learning to Test",
            "content": "Testing is good for the soul.",
            "interactive_hint": "Write a test case."
        }

        # 2. Simulate User Input
        user_feeling = "I feel anxious about testing."
        response = ReflectionService.get_reflection_response(user_feeling)
        
        # 3. Verify Response Structure
        self.assertIsNotNone(response)
        self.assertEqual(response['message'], "I hear you. That sounds tough.")
        self.assertIsNotNone(response.get('new_pattern'))
        self.assertEqual(response['new_pattern']['name'], "Test Pattern")
        
        # 4. Verify Database Persistence
        patterns = get_patterns(user_id=1)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]['pattern_name'], "Test Pattern")
        self.assertEqual(patterns[0]['status'], "new")
        
        print("\nSUCCESS: User flow simulated. Pattern detected, returned in response, and saved to DB.")

if __name__ == '__main__':
    unittest.main()
