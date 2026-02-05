from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, Sale
from datetime import datetime, timedelta
from sqlalchemy import func

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    """Barcha mahsulotlarni qaytaradi"""
    user_id = int(get_jwt_identity())
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([product.to_dict() for product in products]), 200

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Yangi mahsulot yaratadi"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    required_fields = ['name', 'package_type', 'purchase_price', 'sale_price']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Barcha majburiy maydonlar to\'ldirilishi shart'}), 400
    
    product = Product(
        name=data['name'],
        package_type=data['package_type'],
        purchase_price=data['purchase_price'],
        sale_price=data['sale_price'],
        status=data.get('status', 'active')
    )
    
    product.calculate_margin()
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Bitta mahsulotni qaytaradi"""
    user_id = int(get_jwt_identity())
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Mahsulotni yangilaydi"""
    user_id = int(get_jwt_identity())
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if data.get('name'):
        product.name = data['name']
    if data.get('package_type'):
        product.package_type = data['package_type']
    if data.get('purchase_price') is not None:
        product.purchase_price = data['purchase_price']
    if data.get('sale_price') is not None:
        product.sale_price = data['sale_price']
    if data.get('status'):
        product.status = data['status']
    
    product.calculate_margin()
    
    db.session.commit()
    
    return jsonify(product.to_dict()), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Mahsulotni o'chiradi"""
    user_id = int(get_jwt_identity())
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Mahsulot muvaffaqiyatli o\'chirildi'}), 200
