from flask import Flask
from config import Config
from app.dash.dash_app import init_dashboard  # Main dashboard
from app.dash.mba import create_mba_dashboard  # MBA dashboard

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes import main
    app.register_blueprint(main)

    # Initialize Dash apps
    init_dashboard(app)
    create_mba_dashboard(app)

    return app