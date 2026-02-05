from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import os

config_bp = Blueprint('config', __name__)

@config_bp.route('/mapbox-token', methods=['GET'])
@jwt_required()
def get_mapbox_token():
    """Mapbox token'ni qaytaradi"""
    token = os.getenv('MAPBOX_TOKEN', '')
    return jsonify({'token': token}), 200

