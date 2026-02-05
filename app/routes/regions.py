from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Region, Shop, Product, Sale
from datetime import datetime
from sqlalchemy import func

regions_bp = Blueprint('regions', __name__)

@regions_bp.route('', methods=['GET'])
@jwt_required()
def get_regions():
    """Barcha hududlarni qaytaradi"""
    regions = Region.query.order_by(Region.name).all()
    return jsonify([region.to_dict() for region in regions]), 200

@regions_bp.route('', methods=['POST'])
@jwt_required()
def create_region():
    """Yangi hudud yaratadi"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name kiritilishi shart'}), 400
    
    if Region.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Bu hudud allaqachon mavjud'}), 400
    
    import json
    region = Region(
        name=data['name'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        polygon_coordinates=json.dumps(data['polygon_coordinates']) if data.get('polygon_coordinates') else None,
        status=data.get('status', 'planned')
    )
    
    db.session.add(region)
    db.session.commit()
    
    return jsonify(region.to_dict()), 201

@regions_bp.route('/<int:region_id>', methods=['GET'])
@jwt_required()
def get_region(region_id):
    """Bitta hududni qaytaradi"""
    region = Region.query.get_or_404(region_id)
    region_dict = region.to_dict()
    
    # Do'konlar ro'yxati
    shops = Shop.query.filter_by(region_id=region_id).all()
    region_dict['shops'] = [shop.to_dict() for shop in shops]
    
    # Hududdagi mahsulotlar
    product_ids = set()
    for shop in shops:
        for product in shop.products:
            product_ids.add(product.id)
    
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    region_dict['products'] = [p.to_dict() for p in products]
    
    return jsonify(region_dict), 200

@regions_bp.route('/<int:region_id>', methods=['PUT'])
@jwt_required()
def update_region(region_id):
    """Hududni yangilaydi"""
    region = Region.query.get_or_404(region_id)
    data = request.get_json()
    
    if data.get('name'):
        region.name = data['name']
    if data.get('latitude') is not None:
        region.latitude = data['latitude']
    if data.get('longitude') is not None:
        region.longitude = data['longitude']
    if data.get('polygon_coordinates') is not None:
        import json
        region.polygon_coordinates = json.dumps(data['polygon_coordinates']) if isinstance(data['polygon_coordinates'], (list, dict)) else data['polygon_coordinates']
    if data.get('status'):
        region.status = data['status']
    
    region.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(region.to_dict()), 200

@regions_bp.route('/<int:region_id>', methods=['DELETE'])
@jwt_required()
def delete_region(region_id):
    """Hududni o'chiradi"""
    region = Region.query.get_or_404(region_id)
    db.session.delete(region)
    db.session.commit()
    
    return jsonify({'message': 'Hudud muvaffaqiyatli o\'chirildi'}), 200

@regions_bp.route('/map-data', methods=['GET'])
@jwt_required()
def get_map_data():
    """Xarita uchun barcha hududlar ma'lumotlari (markerlar uchun)"""
    regions = Region.query.all()
    result = []
    
    for region in regions:
        shops_count = Shop.query.filter_by(region_id=region.id).count()
        result.append({
            'id': region.id,
            'name': region.name,
            'latitude': float(region.latitude) if region.latitude else None,
            'longitude': float(region.longitude) if region.longitude else None,
            'status': region.status,
            'shops_count': shops_count
        })
    
    return jsonify(result), 200

@regions_bp.route('/occupied-regions', methods=['GET'])
@jwt_required()
def get_occupied_regions():
    """Egallangan hududlar GeoJSON ma'lumotlari"""
    regions = Region.query.filter_by(status='occupied').all()
    result = []
    
    for region in regions:
        import json
        shops_count = Shop.query.filter_by(region_id=region.id).count()
        
        region_data = {
            'id': region.id,
            'name': region.name,
            'status': region.status,
            'shops_count': shops_count,
            'latitude': float(region.latitude) if region.latitude else None,
            'longitude': float(region.longitude) if region.longitude else None
        }
        
        # Agar polygon koordinatalari bo'lsa
        if region.polygon_coordinates:
            try:
                region_data['polygon'] = json.loads(region.polygon_coordinates)
            except:
                region_data['polygon'] = None
        else:
            region_data['polygon'] = None
        
        result.append(region_data)
    
    return jsonify(result), 200

