# app.py

import os
from flask import Flask, jsonify, request, render_template # Note: send_from_directory is removed
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager

# Load environment variables
load_dotenv()

# Initialize Flask app, telling it where to find the static/template files
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- JWT Configuration ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)
# --- END JWT Configuration ---

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# --- END Database Configuration ---


# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# --- Create DB Tables on Startup ---
with app.app_context():
    db.create_all()

# =================================================================
# --- ROUTES TO SERVE FRONTEND PAGES ---
# =================================================================

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/login')
def serve_login():
    return render_template('login.html')

@app.route('/register')
def serve_register():
    return render_template('register.html')

# THE BAD ROUTE HAS BEEN REMOVED. FLASK HANDLES STATIC FILES AUTOMATICALLY.

# =================================================================
# --- API ENDPOINTS ---
# =================================================================

@app.route('/api/register', methods=['POST'])
def register_user():
    # ... (logic is unchanged)
    data = request.get_json();
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    if User.query.filter_by(username=data.get('username')).first(): return jsonify({"error": "Username already exists"}), 409
    new_user = User(username=data.get('username'), password_hash=generate_password_hash(data.get('password')))
    db.session.add(new_user); db.session.commit()
    return jsonify({"message": f"User '{data.get('username')}' created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    # ... (logic is unchanged)
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')): return jsonify({"error": "Invalid username or password"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route('/api/analyze/<coin_symbol>', methods=['GET'])
def analyze_crypto(coin_symbol):
    # ... (logic is unchanged)
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    coin_id = coin_symbol.lower()
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status(); d = r.json()
    except: return jsonify({"error": f"Could not retrieve data for {coin_id}"}), 404
    return jsonify({ "name": d['name'], "current_price": d['market_data']['current_price']['usd'], "ai_analysis": "AI analysis is currently unavailable." })
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)