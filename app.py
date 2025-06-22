# app.py

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# --- FINAL, MOST ROBUST CORS SETTING ---
# This configuration is designed to handle all preflight OPTIONS requests
CORS(app, supports_credentials=True)
# --- END CORS FIX ---

# --- JWT Configuration ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a-default-fallback-secret-key")
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

# --- User Registration Endpoint ---
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 409
    new_user = User(
        username=data.get('username'),
        password_hash=generate_password_hash(data.get('password'), method='pbkdf2:sha256')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User '{data.get('username')}' created successfully"}), 201

# --- User Login Endpoint ---
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# --- Other Endpoints ---
@app.route('/analyze/<coin_symbol>', methods=['GET'])
def analyze_crypto(coin_symbol):
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    if not COINGECKO_API_KEY: return jsonify({"error": "CoinGecko API key missing."}), 500
    coin_id = coin_symbol.lower()
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status()
        d = r.json()
    except: return jsonify({"error": f"Could not retrieve data for {coin_id}. Check ID."}), 404
    return jsonify({
        "coin_symbol": coin_symbol.upper(), "name": d['name'], "current_price": d['market_data']['current_price']['usd'],
        "market_cap": d['market_data']['market_cap']['usd'], "volume_24h": d['market_data']['total_volume']['usd'],
        "ai_analysis": "AI analysis is currently unavailable."
    })

@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = "ok"
    except Exception as e:
        db_status = "error"
    return jsonify({"status": "ok", "message": "Backend is running!", "database_connection": db_status}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)