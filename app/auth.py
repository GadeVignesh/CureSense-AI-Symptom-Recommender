from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import SessionLocal, User
import secrets

bp = Blueprint('auth', __name__)
TOKENS = {}

@bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    db = SessionLocal()
    if db.query(User).filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(username=username, password=generate_password_hash(password))
    db.add(user)
    db.commit()
    return jsonify({'message': 'User registered successfully'})

@bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = secrets.token_hex(16)
    TOKENS[token] = user.username
    return jsonify({'token': token, 'username': user.username})
