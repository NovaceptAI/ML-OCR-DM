# app/main.py

from flask import Flask
from app.routes.document_routes import document_blueprint
from app.config import Config


def create_app():
    # Create a Flask application instance
    app = Flask(__name__)

    # Load configuration from the Config class
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(document_blueprint, url_prefix='/documents')

    # You can add more setup here if needed (e.g., database initialization, login manager setup)

    return app
