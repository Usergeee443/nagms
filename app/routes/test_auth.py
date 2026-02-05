"""
Test endpoint - token muammosini tekshirish uchun
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from app import db
from app.models import User

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-token', methods=['GET'])
@jwt_required()
def test_token():
    """Token test endpoint"""
    try:
        user_id = int(get_jwt_identity())  # String'dan integer'ga o'zgartirish
        user = User.query.get(user_id)
        
        # Authorization header ni ko'rish
        auth_header = request.headers.get('Authorization', '')
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': user.username if user else None,
            'auth_header': auth_header[:50] + '...' if len(auth_header) > 50 else auth_header,
            'message': 'Token to\'g\'ri ishlayapti!'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'auth_header': request.headers.get('Authorization', 'Not found')
        }), 500

