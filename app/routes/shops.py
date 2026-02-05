from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Shop, Region, Product, Sale
from datetime import datetime
from sqlalchemy import func

shops_bp = Blueprint('shops', __name__)

@shops_bp.route('', methods=['GET'])
@jwt_required()
def get_shops():
    """Barcha do'konlarni qaytaradi"""
    shops = Shop.query.order_by(Shop.created_at.desc()).all()
    return jsonify([shop.to_dict() for shop in shops]), 200

@shops_bp.route('', methods=['POST'])
@jwt_required()
def create_shop():
    """Yangi do'kon yaratadi"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('region_id'):
        return jsonify({'error': 'Name va region_id kiritilishi shart'}), 400
    
    shop = Shop(
        name=data['name'],
        region_id=data['region_id'],
        phone=data.get('phone'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        size=data.get('size', 'medium'),
        status=data.get('status', 'active')
    )
    
    db.session.add(shop)
    db.session.commit()
    
    # Mahsulotlarni bog'lash
    if data.get('product_ids'):
        products = Product.query.filter(Product.id.in_(data['product_ids'])).all()
        shop.products = products
        db.session.commit()
    
    return jsonify(shop.to_dict()), 201

@shops_bp.route('/<int:shop_id>', methods=['GET'])
@jwt_required()
def get_shop(shop_id):
    """Bitta do'konni qaytaradi"""
    shop = Shop.query.get_or_404(shop_id)
    shop_dict = shop.to_dict()
    shop_dict['products'] = [p.to_dict() for p in shop.products]
    return jsonify(shop_dict), 200

@shops_bp.route('/<int:shop_id>', methods=['PUT'])
@jwt_required()
def update_shop(shop_id):
    """Do'konni yangilaydi"""
    shop = Shop.query.get_or_404(shop_id)
    data = request.get_json()
    
    if data.get('name'):
        shop.name = data['name']
    if data.get('region_id'):
        shop.region_id = data['region_id']
    if data.get('phone') is not None:
        shop.phone = data['phone']
    if data.get('latitude') is not None:
        shop.latitude = data['latitude']
    if data.get('longitude') is not None:
        shop.longitude = data['longitude']
    if data.get('size'):
        shop.size = data['size']
    if data.get('status'):
        shop.status = data['status']
    
    if data.get('product_ids') is not None:
        products = Product.query.filter(Product.id.in_(data['product_ids'])).all()
        shop.products = products
    
    shop.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(shop.to_dict()), 200

@shops_bp.route('/<int:shop_id>', methods=['DELETE'])
@jwt_required()
def delete_shop(shop_id):
    """Do'konni o'chiradi"""
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    
    return jsonify({'message': 'Do\'kon muvaffaqiyatli o\'chirildi'}), 200

@shops_bp.route('/analysis/top-shops', methods=['GET'])
@jwt_required()
def get_top_shops():
    """Eng ko'p savdo qiladigan do'konlar"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    top_shops = db.session.query(
        Shop.id,
        Shop.name,
        Shop.region_id,
        func.sum(Sale.amount).label('total_amount'),
        func.sum(Sale.quantity).label('total_quantity')
    ).join(Sale).filter(
        Sale.sale_date >= month_start,
        Sale.sale_date <= today
    ).group_by(Shop.id, Shop.name, Shop.region_id).order_by(
        func.sum(Sale.amount).desc()
    ).limit(10).all()
    
    result = []
    for shop in top_shops:
        region = Region.query.get(shop.region_id)
        result.append({
            'id': shop.id,
            'name': shop.name,
            'region_name': region.name if region else None,
            'total_amount': float(shop.total_amount),
            'total_quantity': shop.total_quantity
        })
    
    return jsonify(result), 200

@shops_bp.route('/analysis/top-regions', methods=['GET'])
@jwt_required()
def get_top_regions():
    """Eng kuchli hududlar"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    top_regions = db.session.query(
        Region.id,
        Region.name,
        func.sum(Sale.amount).label('total_amount'),
        func.count(Shop.id.distinct()).label('shops_count')
    ).join(Shop).join(Sale).filter(
        Sale.sale_date >= month_start,
        Sale.sale_date <= today
    ).group_by(Region.id, Region.name).order_by(
        func.sum(Sale.amount).desc()
    ).all()
    
    result = []
    for region in top_regions:
        result.append({
            'id': region.id,
            'name': region.name,
            'total_amount': float(region.total_amount),
            'shops_count': region.shops_count
        })
    
    return jsonify(result), 200

@shops_bp.route('/map-data', methods=['GET'])
@jwt_required()
def get_shops_map_data():
    """Xarita uchun barcha do'konlar ma'lumotlari"""
    shops = Shop.query.filter_by(status='active').all()
    result = []
    
    for shop in shops:
        if shop.latitude and shop.longitude:
            result.append({
                'id': shop.id,
                'name': shop.name,
                'latitude': float(shop.latitude),
                'longitude': float(shop.longitude),
                'region_name': shop.region.name if shop.region else None,
                'phone': shop.phone,
                'size': shop.size,
                'products_count': len(shop.products)
            })
    
    return jsonify(result), 200

