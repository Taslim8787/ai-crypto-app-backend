# app.py

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# THIS IS THE ROBUST CORS SETTING, ALLOWING ALL ROUTES
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# --- END Database Configuration ---


# --- API Keys (loaded from environment variables) ---
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")


# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
# --- END DATABASE MODELS ---


# --- Create DB Tables on Startup (if they don't exist) ---
with app.app_context():
    db.create_all()
    print("Database tables checked/created.")
# --- END WORKAROUND ---


# --- User Registration Endpoint ---
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password, method='pbkdf2:sha256')
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User '{username}' created successfully"}), 201
# --- END: User Registration Endpoint ---

# --- Other Endpoints ---
@app.route('/analyze/<coin_symbol>', methods=['GET'])
def analyze_crypto(coin_symbol):
    if not COINGECKO_API_KEY:
        return jsonify({"error": "CoinGecko API key missing."}), 500
    coin_id = coin_symbol.lower()
    try:
        coin_data_response = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        coin_data_response.raise_for_status()
        coin_data = coin_data_response.json()
    except requests.exceptions.RequestException:
         return jsonify({"error": f"Could not retrieve real-time data for {coin_id}. Check the coin ID."}), 404

    current_price = coin_data['market_data']['current_price']['usd']
    market_cap = coin_data['market_data']['market_cap']['usd']
    volume_24h = coin_data['market_data']['total_volume']['usd']
    name = coin_data['name']
    return jsonify({
        "coin_symbol": coin_symbol.upper(), "name": name, "current_price": current_price,
        "market_cap": market_cap, "volume_24h": volume_24h,
        "ai_analysis": "AI analysis is currently unavailable. Check back later."
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