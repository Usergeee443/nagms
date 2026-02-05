from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Register funksiyasi o'chirildi - faqat bitta admin foydalanuvchi mavjud

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username va password kiritilishi shart'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Noto\'g\'ri username yoki password'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())  # String'dan integer'ga o'zgartirish
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Foydalanuvchi topilmadi'}), 404
    
    return jsonify(user.to_dict()), 200

