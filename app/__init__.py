from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints (routes)
    from app.routes import main
    app.register_blueprint(main)

    # Initialize Database
    from app.db import close_db, init_db
    init_db(app) # Ensure tables exist on startup
    app.teardown_appcontext(close_db)

    return app
