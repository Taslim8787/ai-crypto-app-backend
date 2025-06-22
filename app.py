# app.py - Final Version

import os
from flask import Flask, jsonify, request, render_template, send_from_directory
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager

# Load environment variables
load_dotenv()

# --- Initialize Flask App ---
# This setup correctly tells Flask where to find your frontend files.
app = Flask(__name__, static_folder='static', template_folder='templates')

# --- JWT Configuration ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    __tablename__ = 'users' # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# --- Create DB Tables on Startup ---
with app.app_context():
    db.create_all()
    print("Database tables checked/created.")

# =================================================================
# --- ROUTES TO SERVE FRONTEND HTML PAGES ---
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

# =================================================================
# --- API ENDPOINTS (prefixed with /api/) ---
# =================================================================

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'): 
        return jsonify({"error": "Username and password required"}), 400
    if User.query.filter_by(username=data.get('username')).first(): 
        return jsonify({"error": "Username already exists"}), 409
    
    new_user = User(
        username=data.get('username'), 
        password_hash=generate_password_hash(data.get('password'))
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User '{data.get('username')}' created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'): 
        return jsonify({"error": "Username and password required"}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"error": "Invalid username or password"}), 401
        
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route('/api/analyze/<coin_id>', methods=['GET'])
def analyze_crypto(coin_id):
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}"
        headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        d = r.json()
        
        response_data = {
            "name": d.get('name'),
            "current_price": d.get('market_data', {}).get('current_price', {}).get('usd'),
            "ai_analysis": "AI analysis is currently unavailable."
        }
        return jsonify(response_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from CoinGecko: {e}")
        return jsonify({"error": f"Could not retrieve data for {coin_id}. Check ID."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)