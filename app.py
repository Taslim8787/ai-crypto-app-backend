# app.py

import os
from flask import Flask, jsonify, request, render_template
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager # jwt_required and get_jwt_identity are new

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configurations (JWT, Database) ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
db = SQLAlchemy(app)

# =================================================================
# --- DATABASE MODELS ---
# =================================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # This creates a relationship, so we can easily get all watchlist items for a user
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True)

# --- NEW: WatchlistItem Model ---
class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False) # e.g., 'bitcoin', 'ethereum'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Link to the User table

    def serialize(self):
        """Return object data in a easily serializable format"""
        return {'id': self.id, 'coin_id': self.coin_id}
# --- END NEW MODEL ---

# --- Create DB Tables on Startup ---
with app.app_context():
    db.create_all()
    print("Database tables checked/created.")

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
    
# --- NEW: Route for the watchlist page ---
@app.route('/watchlist')
def serve_watchlist():
    return render_template('watchlist.html')

# =================================================================
# --- API ENDPOINTS ---
# =================================================================

# --- Auth Endpoints (No Change) ---
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
    
# --- Analysis Endpoint (No Change) ---
@app.route('/api/analyze/<coin_id>', methods=['GET'])
def analyze_crypto(coin_id):
    # ... (logic is unchanged)
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status(); d = r.json()
    except: return jsonify({"error": f"Could not retrieve data for {coin_id}"}), 404
    return jsonify({ "name": d.get('name'), "current_price": d.get('market_data', {}).get('current_price', {}).get('usd'), "ai_analysis": "AI analysis is currently unavailable." })


# --- NEW: Watchlist API Endpoints ---
@app.route('/api/watchlist', methods=['GET'])
@jwt_required() # This protects the route, only logged-in users can access
def get_watchlist():
    current_user_id = get_jwt_identity() # Get user ID from their access token
    watchlist_items = WatchlistItem.query.filter_by(user_id=current_user_id).all()
    # Convert the list of objects to a list of dictionaries
    return jsonify([item.serialize() for item in watchlist_items])

@app.route('/api/watchlist/add', methods=['POST'])
@jwt_required() # Protect this route
def add_to_watchlist():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('coin_id'):
        return jsonify({"error": "Coin ID is required"}), 400
    
    coin_id = data.get('coin_id').lower()

    # Check if the coin is already in the user's watchlist
    existing_item = WatchlistItem.query.filter_by(user_id=current_user_id, coin_id=coin_id).first()
    if existing_item:
        return jsonify({"message": "Coin already in watchlist"}), 200

    # Add the new item
    new_item = WatchlistItem(coin_id=coin_id, user_id=current_user_id)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({"message": f"Added {coin_id} to watchlist"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)