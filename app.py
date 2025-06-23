# app.py

import os
from flask import Flask, jsonify, request, render_template, session
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime # New import for trade timestamps

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- Configurations ---
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =================================================================
# --- DATABASE MODELS ---
# =================================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True, cascade="all, delete-orphan")
    portfolio = db.relationship('PortfolioItem', backref='user', lazy=True, cascade="all, delete-orphan")
    trades = db.relationship('Trade', backref='user', lazy=True, cascade="all, delete-orphan") # <-- NEW

class WatchlistItem(db.Model):
    # ... (unchanged)
    __tablename__ = 'watchlist_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def serialize(self): return {'id': self.id, 'coin_id': self.coin_id}

class PortfolioItem(db.Model):
    # ... (unchanged)
    __tablename__ = 'portfolio_items'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def serialize(self): return {'id': self.id, 'coin_id': self.coin_id, 'amount': self.amount, 'buy_price': self.buy_price}

# --- NEW: Trade Model ---
class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(100), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=False)
    trade_type = db.Column(db.String(10), nullable=False) # 'long' or 'short'
    outcome = db.Column(db.String(10), nullable=False) # 'win' or 'loss'
    trade_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def serialize(self):
        return {
            'id': self.id, 'coin_id': self.coin_id, 'entry_price': self.entry_price,
            'exit_price': self.exit_price, 'trade_type': self.trade_type,
            'outcome': self.outcome, 'trade_date': self.trade_date.strftime('%Y-%m-%d %H:%M:%S')
        }
# --- END NEW MODEL ---

with app.app_context():
    db.create_all()

# --- Custom Decorator for Login Check ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# =================================================================
# --- Frontend Routes ---
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

# --- NEW: Route for the trades page ---
@app.route('/trades')
def serve_trades():
    return render_template('trades.html')

# =================================================================
# --- API ENDPOINTS ---
# =================================================================

# Auth, Watchlist, Portfolio, Analyze, Get-Prices Endpoints (Unchanged)
# ... (all previous API endpoints are here and unchanged) ...
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
    session['user_id'] = user.id
    return jsonify({"message": "Login successful"})

@app.route('/api/logout', methods=['POST'])
def logout_user():
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"})

@app.route('/api/watchlist', methods=['GET'])
@login_required
def get_watchlist():
    current_user_id = session['user_id']
    items = WatchlistItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.serialize() for item in items])

@app.route('/api/watchlist/add', methods=['POST'])
@login_required
def add_to_watchlist():
    current_user_id = session['user_id']
    data = request.get_json(); coin_id = data.get('coin_id')
    if not coin_id: return jsonify({"error": "Missing 'coin_id'"}), 400
    existing = WatchlistItem.query.filter_by(user_id=current_user_id, coin_id=coin_id.lower()).first()
    if existing: return jsonify({"message": f"{coin_id} is already in watchlist"}), 200
    new_item = WatchlistItem(coin_id=coin_id.lower(), user_id=current_user_id)
    db.session.add(new_item); db.session.commit()
    return jsonify({"message": f"Added {coin_id} to watchlist"}), 201

@app.route('/api/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    current_user_id = session['user_id']
    items = PortfolioItem.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.serialize() for item in items])

@app.route('/api/portfolio/add', methods=['POST'])
@login_required
def add_to_portfolio():
    current_user_id = session['user_id']
    data = request.get_json()
    if not data or not data.get('coin_id') or not data.get('amount') or not data.get('buy_price'): return jsonify({"error": "Missing fields"}), 400
    new_item = PortfolioItem(coin_id=data['coin_id'].lower(), amount=float(data['amount']), buy_price=float(data['buy_price']), user_id=current_user_id)
    db.session.add(new_item); db.session.commit()
    return jsonify({"message": "Added to portfolio"}), 201

@app.route('/api/get-prices', methods=['POST'])
@login_required
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

@app.route('/api/analyze/<coin_id>', methods=['GET'])
def analyze_crypto(coin_id):
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}", headers={"x-cg-demo-api-key": COINGECKO_API_KEY})
        r.raise_for_status(); d = r.json()
    except: return jsonify({"error": f"Could not retrieve data for {coin_id}"}), 404
    return jsonify({ "name": d.get('name'), "current_price": d.get('market_data', {}).get('current_price', {}).get('usd'), "ai_analysis": "AI analysis is currently unavailable." })

# --- NEW: Trade Logger API Endpoints ---
@app.route('/api/trades', methods=['GET'])
@login_required
def get_trades():
    current_user_id = session['user_id']
    trades = Trade.query.filter_by(user_id=current_user_id).order_by(Trade.trade_date.desc()).all()
    return jsonify([trade.serialize() for trade in trades])

@app.route('/api/trades/add', methods=['POST'])
@login_required
def log_trade():
    current_user_id = session['user_id']
    data = request.get_json()
    
    required_fields = ['coin_id', 'entry_price', 'exit_price', 'trade_type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        entry = float(data['entry_price'])
        exit = float(data['exit_price'])
        trade_type = data['trade_type']
        
        # Determine outcome
        if trade_type == 'long' and exit > entry:
            outcome = 'win'
        elif trade_type == 'short' and entry > exit:
            outcome = 'win'
        else:
            outcome = 'loss'

        new_trade = Trade(
            coin_id=data['coin_id'].lower(),
            entry_price=entry,
            exit_price=exit,
            trade_type=trade_type,
            outcome=outcome,
            user_id=current_user_id
        )
        db.session.add(new_trade)
        db.session.commit()
        return jsonify({"message": "Trade logged successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {e}"}), 500
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)