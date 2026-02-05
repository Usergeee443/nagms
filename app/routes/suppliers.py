from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Supplier, Product, Sale
from datetime import datetime
from sqlalchemy import func

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('', methods=['GET'])
@jwt_required()
def get_suppliers():
    """Barcha ta'minotchilarni qaytaradi"""
    suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    return jsonify([supplier.to_dict() for supplier in suppliers]), 200

@suppliers_bp.route('', methods=['POST'])
@jwt_required()
def create_supplier():
    """Yangi ta'minotchi yaratadi"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name kiritilishi shart'}), 400
    
    supplier = Supplier(
        name=data['name'],
        country=data.get('country'),
        region=data.get('region'),
        product_type=data.get('product_type'),
        price_level=data.get('price_level'),
        reliability_rating=data.get('reliability_rating', 3),
        contact_info=data.get('contact_info'),
        notes=data.get('notes')
    )
    
    db.session.add(supplier)
    db.session.commit()
    
    return jsonify(supplier.to_dict()), 201

@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    """Bitta ta'minotchini qaytaradi"""
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify(supplier.to_dict()), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    """Ta'minotchini yangilaydi"""
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json()
    
    if data.get('name'):
        supplier.name = data['name']
    if data.get('country') is not None:
        supplier.country = data['country']
    if data.get('region') is not None:
        supplier.region = data['region']
    if data.get('product_type') is not None:
        supplier.product_type = data['product_type']
    if data.get('price_level') is not None:
        supplier.price_level = data['price_level']
    if data.get('reliability_rating') is not None:
        supplier.reliability_rating = data['reliability_rating']
    if data.get('contact_info') is not None:
        supplier.contact_info = data['contact_info']
    if data.get('notes') is not None:
        supplier.notes = data['notes']
    
    supplier.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(supplier.to_dict()), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    """Ta'minotchini o'chiradi"""
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    
    return jsonify({'message': 'Ta\'minotchi muvaffaqiyatli o\'chirildi'}), 200

@suppliers_bp.route('/analysis/most-profitable', methods=['GET'])
@jwt_required()
def get_most_profitable():
    """Eng foydali ta'minotchilar"""
    suppliers = Supplier.query.all()
    result = []
    
    for supplier in suppliers:
        products = Product.query.filter_by(supplier_id=supplier.id, status='active').all()
        total_profit = 0
        total_sales = 0
        
        for product in products:
            if product.purchase_price and product.sale_price:
                profit_per_unit = float(product.sale_price) - float(product.purchase_price)
                # Oxirgi oy savdo miqdorini olish
                from datetime import timedelta
                today = datetime.now().date()
                month_start = today.replace(day=1)
                sales = Sale.query.filter_by(product_id=product.id).filter(
                    Sale.sale_date >= month_start
                ).all()
                
                for sale in sales:
                    total_profit += profit_per_unit * sale.quantity
                    total_sales += float(sale.amount)
        
        result.append({
            'id': supplier.id,
            'name': supplier.name,
            'total_profit': round(total_profit, 2),
            'total_sales': round(total_sales, 2),
            'products_count': len(products),
            'reliability_rating': supplier.reliability_rating
        })
    
    result.sort(key=lambda x: x['total_profit'], reverse=True)
    return jsonify(result), 200

@suppliers_bp.route('/analysis/risky', methods=['GET'])
@jwt_required()
def get_risky_suppliers():
    """Riskli ta'minotchilar (reliability_rating < 3)"""
    risky_suppliers = Supplier.query.filter(Supplier.reliability_rating < 3).all()
    return jsonify([supplier.to_dict() for supplier in risky_suppliers]), 200

