from flask import Blueprint, render_template, request, jsonify
from app.services import ReflectionService, ContentService, DiscoveryService, LearningHubService
from app.db import get_recent_history, get_all_learning_topics, update_topic_progress

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Renders the landing page."""
    return render_template('index.html')

@main.route('/feeling', methods=['GET', 'POST'])
def feeling():
    """Handles the emotion input page."""
    if request.method == 'POST':
        user_feeling = request.form.get('feeling')
        # Redirect to reflection with the feeling as a query param or state
        # In this new "chat" model, we might just pass the initial seed
        return render_template('reflection.html', initial_feeling=user_feeling)
    return render_template('feeling.html')

@main.route('/reflection')
def reflection():
    """Renders the reflection page."""
    return render_template('reflection.html')

@main.route('/discoveries')
def discoveries():
    """Renders the Discoveries Panel."""
    return render_template('discoveries.html')

@main.route('/api/discoveries')
def api_discoveries():
    """API endpoint to get all user discoveries (patterns + topics)."""
    data = DiscoveryService.get_user_discoveries(user_id=1)
    return jsonify(data)

@main.route('/api/patterns/<int:pattern_id>/ack', methods=['PATCH'])
def api_ack_pattern(pattern_id):
    """API endpoint to acknowledge/update pattern status."""
    data = request.get_json()
    status = data.get('status')
    if status not in ['new', 'acknowledged', 'working_on_it', 'explored']:
        return jsonify({"error": "Invalid status"}), 400
        
    DiscoveryService.acknowledge_pattern(pattern_id, status, user_id=1)
    return jsonify({"success": True})

@main.route('/api/reflect', methods=['POST'])
def api_reflect():
    """API endpoint for AI reflection."""
    data = request.get_json()
    user_feeling = data.get('feeling', '')
    if not user_feeling:
        return jsonify({"error": "No feeling provided"}), 400
    
    response = ReflectionService.get_reflection_response(user_feeling)
    return jsonify(response)

@main.route('/api/history')
def api_history():
    """Returns recent chat history."""
    history = get_recent_history(limit=20)
    # Format for frontend (ensure roles match css classes)
    formatted = []
    for msg in history:
        css_class = 'user-message' if msg['role'] == 'user' else 'ai-message'
        formatted.append({
            "message": msg['content'],
            "class": css_class
        })
    return jsonify(formatted)

@main.route('/learning-hub')
def learning_hub():
    """Renders the new AI-driven Learning Hub."""
    return render_template('learning_hub.html')

@main.route('/api/learning-topics')
def api_learning_topics():
    """API endpoint to get all learning topics for user."""
    topics = get_all_learning_topics(user_id=1)
    return jsonify(topics)

@main.route('/api/learning-topics/<int:topic_id>/progress', methods=['PATCH'])
def api_update_topic_progress(topic_id):
    """API endpoint to update topic progress."""
    data = request.get_json()
    status = data.get('status')
    if status not in ['unread', 'in_progress', 'completed']:
        return jsonify({"error": "Invalid status"}), 400
    
    update_topic_progress(topic_id, status, user_id=1)
    return jsonify({"success": True})
