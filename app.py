# app.py - Final Watchlist Fix

import os
from flask import Flask, jsonify, request, render_template
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

# Initialize App and Configs
load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True, cascade="all, delete-orphan")

class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'coin_id', name='_user_coin_uc'),) # Prevents duplicates

    def serialize(self):
        return {'id': self.id, 'coin_id': self.coin_id}

# --- Create DB Tables on Startup ---
with app.app_context():
    db.create_all()

# --- Frontend Routes ---
@app.route('/')
def serve_index(): return render_template('index.html')
@app.route('/login')
def serve_login(): return render_template('login.html')
@app.route('/register')
def serve_register(): return render_template('register.html')
@app.route('/watchlist')
def serve_watchlist(): return render_template('watchlist.html')

# --- API ENDPOINTS ---

# Auth Endpoints (Unchanged)
@app.route('/api/register', methods=['POST'])
def register_user():
    # ... logic unchanged
    data = request.get_json();
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    if User.query.filter_by(username=data.get('username')).first(): return jsonify({"error": "Username already exists"}), 409
    new_user = User(username=data.get('username'), password_hash=generate_password_hash(data.get('password')))
    db.session.add(new_user); db.session.commit()
    return jsonify({"message": f"User '{data.get('username')}' created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    # ... logic unchanged
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')): return jsonify({"error": "Invalid username or password"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)
    
# Analysis Endpoint (Unchanged)
@app.route('/api/analyze/<coin_id>', methods=['GET'])
def analyze_crypto(coin_id):
    # ... logic unchanged
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status(); d = r.json()
    except: return jsonify({"error": f"Could not retrieve data for {coin_id}"}), 404
    return jsonify({ "coin_symbol": d.get('symbol', '').upper(), "name": d.get('name'), "current_price": d.get('market_data', {}).get('current_price', {}).get('usd'), "ai_analysis": "AI analysis is currently unavailable." })


# Watchlist GET Endpoint (Unchanged)
@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    current_user_id = get_jwt_identity()
    watchlist_items = WatchlistItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.serialize() for item in watchlist_items])

# --- MOST ROBUST Watchlist ADD Endpoint ---
@app.route('/api/watchlist/add', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    current_user_id = get_jwt_identity()
    
    # Check if the request has a JSON body
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    coin_id = data.get('coin_id', None)

    if not coin_id:
        return jsonify({"error": "Missing 'coin_id' in request body"}), 400
    
    coin_id = coin_id.lower()

    try:
        # Check if the coin is already in the user's watchlist
        existing_item = WatchlistItem.query.filter_by(user_id=current_user_id, coin_id=coin_id).first()
        if existing_item:
            return jsonify({"message": f"{coin_id.capitalize()} is already in your watchlist"}), 200

        # If not, create and add the new item
        new_item = WatchlistItem(coin_id=coin_id, user_id=current_user_id)
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({"message": f"Added {coin_id.capitalize()} to watchlist"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)