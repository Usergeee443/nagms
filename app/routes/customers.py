from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Customer
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """Barcha mijozlarni qaytaradi"""
    user_id = int(get_jwt_identity())
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return jsonify([customer.to_dict() for customer in customers]), 200

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """Yangi mijoz yaratadi"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Ism kiritilishi shart'}), 400
    
    customer = Customer(
        name=data['name'],
        additional_name=data.get('additional_name'),
        phone=data.get('phone'),
        address=data.get('address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Bitta mijozni qaytaradi"""
    user_id = int(get_jwt_identity())
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Mijozni yangilaydi"""
    user_id = int(get_jwt_identity())
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    if data.get('name'):
        customer.name = data['name']
    if 'additional_name' in data:
        customer.additional_name = data.get('additional_name')
    if 'phone' in data:
        customer.phone = data.get('phone')
    if 'address' in data:
        customer.address = data.get('address')
    if 'latitude' in data:
        customer.latitude = data.get('latitude')
    if 'longitude' in data:
        customer.longitude = data.get('longitude')
    
    customer.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """Mijozni o'chiradi"""
    user_id = int(get_jwt_identity())
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({'message': 'Mijoz muvaffaqiyatli o\'chirildi'}), 200

@customers_bp.route('/map-data', methods=['GET'])
@jwt_required()
def get_map_data():
    """Xarita uchun mijozlar ma'lumotlari"""
    user_id = int(get_jwt_identity())
    customers = Customer.query.filter(
        Customer.latitude.isnot(None),
        Customer.longitude.isnot(None)
    ).all()
    
    result = []
    for customer in customers:
        result.append({
            'id': customer.id,
            'name': customer.name,
            'additional_name': customer.additional_name,
            'phone': customer.phone,
            'address': customer.address,
            'latitude': float(customer.latitude),
            'longitude': float(customer.longitude)
        })
    
    return jsonify(result), 200
