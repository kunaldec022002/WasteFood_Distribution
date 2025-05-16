import os
import logging
import json
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Create data directories if they don't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize data files if they don't exist
if not os.path.exists('data/users.json'):
    with open('data/users.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/food_listings.json'):
    with open('data/food_listings.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/pickups.json'):
    with open('data/pickups.json', 'w') as f:
        json.dump([], f)

# Set up the app configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.jinja_env.globals.update(hasattr=hasattr)

# Import routes after app is initialized to avoid circular imports
from models import User
from routes import *

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(int(user_id))

# Custom Jinja filters
@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d'):
    if not value:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.strftime(format)

@app.template_filter('days_remaining')
def days_remaining(expiration_date):
    if not expiration_date:
        return 0
    if isinstance(expiration_date, str):
        expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
    delta = expiration_date - datetime.now()
    return max(0, delta.days)
