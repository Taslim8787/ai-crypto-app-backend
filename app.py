# app.py

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # For password security

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# --- END Database Configuration ---


# --- API Keys (loaded from environment variables) ---
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# --- DEBUG LINES ---
print(f"DEBUG: CoinGecko API Key loaded: {'Yes' if COINGECKO_API_KEY else 'No'}")
print(f"DEBUG: Database URL loaded: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")
# --- END DEBUG LINES ---


# --- DATABASE MODELS ---
# This defines the "User" table in our database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
# --- END DATABASE MODELS ---


# This is a one-time command to create the database tables.
# We will run this manually using the Render Shell.
@app.cli.command("create-db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    print("Database tables created.")


# --- Helper Functions (No Change) ---
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinGecko data for {coin_id}: {e}")
        return None

# --- API Endpoints ---
@app.route('/analyze/<coin_symbol>', methods=['GET'])
def analyze_crypto(coin_symbol):
    # This function remains the same
    # ... (code is unchanged, so omitting for brevity)
    if not COINGECKO_API_KEY:
        return jsonify({"error": "CoinGecko API key missing."}), 500
    coin_id = coin_symbol.lower()
    coin_data = get_coin_data(coin_id)
    if not coin_data:
        return jsonify({"error": f"Could not retrieve real-time data for {coin_id}. Check the coin ID."}), 404
    current_price = coin_data['market_data']['current_price']['usd']
    market_cap = coin_data['market_data']['market_cap']['usd']
    volume_24h = coin_data['market_data']['total_volume']['usd']
    name = coin_data['name']
    return jsonify({
        "coin_symbol": coin_symbol.upper(),
        "name": name,
        "current_price": current_price,
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "ai_analysis": "AI analysis is currently unavailable. Check back later."
    })

@app.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute('SELECT 1')
        db_status = "ok"
    except Exception as e:
        print(f"Database connection error: {e}")
        db__status = "error"
    return jsonify({
        "status": "ok",
        "message": "Backend is running!",
        "database_connection": db_status
    }), 200

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)