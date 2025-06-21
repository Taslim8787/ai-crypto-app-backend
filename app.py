# app.py

import os
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy # <-- NEW IMPORT

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all routes for simplicity

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # <-- INITIALIZE DATABASE
# --- END Database Configuration ---


# --- API Keys (loaded from environment variables) ---
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# --- DEBUG LINES ---
print(f"DEBUG: CoinGecko API Key loaded: {'Yes' if COINGECKO_API_KEY else 'No'}")
print(f"DEBUG: Database URL loaded: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")
# --- END DEBUG LINES ---


# --- Helper Functions to Fetch Data ---

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

# --- Main API Endpoint for Crypto Data ---

@app.route('/analyze/<coin_symbol>', methods=['GET'])
def analyze_crypto(coin_symbol):
    # This function remains the same for now
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

# --- Simple Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = "ok"
    except Exception as e:
        print(f"Database connection error: {e}")
        db_status = "error"
    
    return jsonify({
        "status": "ok",
        "message": "Backend is running!",
        "database_connection": db_status
    }), 200

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)