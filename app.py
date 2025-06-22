# app.py - Final Corrected Version

import os
from flask import Flask, jsonify, request, render_template
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configurations ---
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
    portfolio = db.relationship('PortfolioItem', backref='user', lazy=True, cascade="all, delete-orphan")

class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def serialize(self): return {'id': self.id, 'coin_id': self.coin_id}

class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def serialize(self): return {'id': self.id, 'coin_id': self.coin_id, 'amount': self.amount, 'buy_price': self.buy_price}

# --- Create DB Tables on Startup ---
with app.app_context():
    db.create_all()

# =================================================================
# --- ROUTES TO SERVE FRONTEND HTML PAGES ---
# =================================================================

@app.route('/')
def serve_index(): return render_template('index.html')
@app.route('/login')
def serve_login(): return render_template('login.html')
@app.route('/register')
def serve_register(): return render_template('register.html')
@app.route('/watchlist')
def serve_watchlist(): return render_template('watchlist.html')
@app.route('/portfolio')
def serve_portfolio(): return render_template('portfolio.html')

# =================================================================
# --- API ENDPOINTS ---
# =================================================================

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json();
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    if User.query.filter_by(username=data.get('username')).first(): return jsonify({"error": "Username already exists"}), 409
    new_user = User(username=data.get('username'), password_hash=generate_password_hash(data.get('password')))
    db.session.add(new_user); db.session.commit()
    return jsonify({"message": f"User '{data.get('username')}' created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'): return jsonify({"error": "Username and password required"}), 400
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')): return jsonify({"error": "Invalid username or password"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout_user():
    # In a real app, you might want to blacklist the token, but for now, this is fine
    return jsonify({"message": "Logout successful"})


# --- THIS IS THE CORRECTED ANALYZE FUNCTION ---
@app.route('/api/analyze/<string:coin_id>', methods=['GET'])
def analyze_crypto(coin_id): # <-- The variable name now correctly matches the route
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}"
        headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}
        r = requests.get(url, headers=headers)
        r.raise_for_status() # This will raise an error for 4xx or 5xx responses
        d = r.json()
        
        response_data = {
            "name": d.get('name'),
            "current_price": d.get('market_data', {}).get('current_price', {}).get('usd'),
            "ai_analysis": "AI analysis is currently unavailable."
        }
        return jsonify(response_data)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return jsonify({"error": f"Coin ID '{coin_id}' not found on CoinGecko."}), 404
        else:
            return jsonify({"error": f"Error from CoinGecko: {err}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
# --- END CORRECTION ---

@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    current_user_id = get_jwt_identity()
    items = WatchlistItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.serialize() for item in items])

@app.route('/api/watchlist/add', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    current_user_id = get_jwt_identity()
    data = request.get_json(); coin_id = data.get('coin_id')
    if not coin_id: return jsonify({"error": "Missing 'coin_id'"}), 400
    existing = WatchlistItem.query.filter_by(user_id=current_user_id, coin_id=coin_id.lower()).first()
    if existing: return jsonify({"message": f"{coin_id} is already in watchlist"}), 200
    new_item = WatchlistItem(coin_id=coin_id.lower(), user_id=current_user_id)
    db.session.add(new_item); db.session.commit()
    return jsonify({"message": f"Added {coin_id} to watchlist"}), 201

@app.route('/api/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    current_user_id = get_jwt_identity()
    items = PortfolioItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.serialize() for item in items])

@app.route('/api/portfolio/add', methods=['POST'])
@jwt_required()
def add_to_portfolio():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('coin_id') or not data.get('amount') or not data.get('buy_price'): return jsonify({"error": "Missing fields"}), 400
    new_item = PortfolioItem(coin_id=data['coin_id'].lower(), amount=float(data['amount']), buy_price=float(data['buy_price']), user_id=current_user_id)
    db.session.add(new_item); db.session.commit()
    return jsonify({"message": "Added to portfolio"}), 201

@app.route('/api/get-prices', methods=['POST'])
@jwt_required() # Protect this endpoint
def get_prices():
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids: return jsonify({})
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    ids_string = ",".join(ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"
    try:
        r = requests.get(url, headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status(); prices = r.json()
        return jsonify(prices)
    except: return jsonify({"error": "Could not fetch prices"}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)