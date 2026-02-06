from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Sale, OnlineSale, Customer, Product
from datetime import datetime, timedelta
from sqlalchemy import func, extract

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('', methods=['GET'])
@jwt_required()
def get_sales():
    """Barcha savdolarni qaytaradi"""
    user_id = int(get_jwt_identity())
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    
    if start_date:
        query = query.filter(Sale.sale_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.sale_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    sales = query.order_by(Sale.sale_date.desc()).all()
    return jsonify([sale.to_dict() for sale in sales]), 200

@sales_bp.route('', methods=['POST'])
@jwt_required()
def create_sale():
    """Yangi savdo yaratadi — savdo paytida dona narxi, xarid narxi va foyda avtomatik saqlanadi (mahsulot narxi keyin o'zgasa ham ta'sir qilmaydi)"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('customer_id') or not data.get('product_id') or not data.get('amount'):
        return jsonify({'error': 'customer_id, product_id va amount kiritilishi shart'}), 400
    
    quantity = data.get('quantity', 1)
    amount = float(data['amount'])
    product = Product.query.get(data['product_id'])
    # Xarid narxi: foydalanuvchi kiritgan bo'lsa shuni ishlatamiz (oldingi narx — sof foyda aniq bo'ladi)
    purchase_price_at_sale = data.get('purchase_price_at_sale')
    if purchase_price_at_sale is not None:
        purchase_price_at_sale = float(purchase_price_at_sale)
    elif product and product.purchase_price is not None:
        purchase_price_at_sale = float(product.purchase_price)
    else:
        purchase_price_at_sale = 0
    unit_price = round(amount / quantity, 2) if quantity else 0
    profit = round(amount - (purchase_price_at_sale * quantity), 2)
    sale = Sale(
        customer_id=data['customer_id'],
        product_id=data['product_id'],
        quantity=quantity,
        amount=amount,
        unit_price=unit_price,
        purchase_price_at_sale=purchase_price_at_sale,
        profit=profit,
        sale_date=datetime.strptime(data.get('sale_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    )
    db.session.add(sale)
    db.session.commit()
    return jsonify(sale.to_dict()), 201

@sales_bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """Bitta savdoni qaytaradi"""
    user_id = int(get_jwt_identity())
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(sale.to_dict()), 200

@sales_bp.route('/<int:sale_id>', methods=['PUT'])
@jwt_required()
def update_sale(sale_id):
    """Savdoni yangilaydi — mavjud savdoda saqlangan xarid narxi va foyda yangilanadi (mahsulotning hozirgi narxi emas)"""
    user_id = int(get_jwt_identity())
    sale = Sale.query.get_or_404(sale_id)
    data = request.get_json()
    
    if data.get('customer_id'):
        sale.customer_id = data['customer_id']
    if data.get('product_id'):
        sale.product_id = data['product_id']
    if data.get('quantity') is not None:
        sale.quantity = data['quantity']
    if data.get('amount') is not None:
        sale.amount = data['amount']
    if data.get('sale_date'):
        sale.sale_date = datetime.strptime(data['sale_date'], '%Y-%m-%d').date()
    # Xarid narxi (tan narx, savdo paytida): frontend yuborsa shu qiymat saqlanadi
    if 'purchase_price_at_sale' in data:
        raw = data['purchase_price_at_sale']
        if raw is None or raw == '':
            purchase = None
        else:
            try:
                purchase = float(raw)
            except (TypeError, ValueError):
                purchase = None
        sale.purchase_price_at_sale = purchase
    else:
        purchase = sale.purchase_price_at_sale
        if purchase is None and sale.product_id:
            product = Product.query.get(sale.product_id)
            purchase = float(product.purchase_price) if product and product.purchase_price is not None else 0
            sale.purchase_price_at_sale = purchase
        else:
            purchase = float(purchase) if purchase is not None else 0
    sale.unit_price = round(float(sale.amount) / (sale.quantity or 1), 2) if sale.quantity else None
    sale.profit = round(float(sale.amount) - (float(purchase or 0) * (sale.quantity or 0)), 2)
    db.session.commit()
    return jsonify(sale.to_dict()), 200

@sales_bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_sale(sale_id):
    """Savdoni o'chiradi"""
    user_id = int(get_jwt_identity())
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    
    return jsonify({'message': 'Savdo muvaffaqiyatli o\'chirildi'}), 200

@sales_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Savdo statistikasi"""
    user_id = int(get_jwt_identity())
    period = request.args.get('period', 'month')
    
    today = datetime.now().date()
    
    if period == 'day':
        start_date = today
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = today.replace(day=1)
        end_date = today
    
    total_sales = db.session.query(func.sum(Sale.amount)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    total_quantity = db.session.query(func.sum(Sale.quantity)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    if period == 'month':
        last_month_start = (start_date - timedelta(days=1)).replace(day=1)
        last_month_end = start_date - timedelta(days=1)
        last_month_sales = db.session.query(func.sum(Sale.amount)).filter(
            Sale.sale_date >= last_month_start,
            Sale.sale_date <= last_month_end
        ).scalar() or 0
        
        growth_percent = 0
        if last_month_sales > 0:
            growth_percent = ((float(total_sales) - float(last_month_sales)) / float(last_month_sales)) * 100
    else:
        growth_percent = 0
    
    return jsonify({
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_sales': float(total_sales),
        'total_quantity': int(total_quantity),
        'growth_percent': round(growth_percent, 2)
    }), 200

@sales_bp.route('/online', methods=['GET'])
@jwt_required()
def get_online_sales():
    """Barcha online savdolarni qaytaradi"""
    user_id = int(get_jwt_identity())
    online_sales = OnlineSale.query.order_by(OnlineSale.sale_date.desc()).all()
    return jsonify([sale.to_dict() for sale in online_sales]), 200

@sales_bp.route('/online', methods=['POST'])
@jwt_required()
def create_online_sale():
    """Yangi online savdo yaratadi"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('platform') or not data.get('amount'):
        return jsonify({'error': 'platform va amount kiritilishi shart'}), 400
    
    online_sale = OnlineSale(
        platform=data['platform'],
        product_id=data.get('product_id'),
        quantity=data.get('quantity', 1),
        amount=data['amount'],
        sale_date=datetime.strptime(data.get('sale_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    )
    
    db.session.add(online_sale)
    db.session.commit()
    
    return jsonify(online_sale.to_dict()), 201

@sales_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_sales():
    """Tarixiy ma'lumotlarni bulk import qilish"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('sales') or not isinstance(data['sales'], list):
        return jsonify({'error': 'sales array kiritilishi shart'}), 400
    
    created_sales = []
    errors = []
    
    for idx, sale_data in enumerate(data['sales']):
        try:
            if not sale_data.get('customer_id') or not sale_data.get('product_id') or not sale_data.get('amount'):
                errors.append(f'Qator {idx + 1}: customer_id, product_id va amount kiritilishi shart')
                continue
            
            customer = Customer.query.get(sale_data['customer_id'])
            product = Product.query.get(sale_data['product_id'])
            
            if not customer:
                errors.append(f'Qator {idx + 1}: Mijoz topilmadi (ID: {sale_data["customer_id"]})')
                continue
            
            if not product:
                errors.append(f'Qator {idx + 1}: Mahsulot topilmadi (ID: {sale_data["product_id"]})')
                continue
            
            sale_date = datetime.now().date()
            if sale_data.get('sale_date'):
                try:
                    sale_date = datetime.strptime(sale_data['sale_date'], '%Y-%m-%d').date()
                except ValueError:
                    errors.append(f'Qator {idx + 1}: Noto\'g\'ri sana formati')
                    continue
            
            quantity = sale_data.get('quantity', 1)
            amount = float(sale_data['amount'])
            purchase_price_at_sale = sale_data.get('purchase_price_at_sale')
            if purchase_price_at_sale is not None:
                purchase_price_at_sale = float(purchase_price_at_sale)
            elif product.purchase_price is not None:
                purchase_price_at_sale = float(product.purchase_price)
            else:
                purchase_price_at_sale = 0
            unit_price = round(amount / quantity, 2) if quantity else 0
            profit = round(amount - (purchase_price_at_sale * quantity), 2)
            sale = Sale(
                customer_id=sale_data['customer_id'],
                product_id=sale_data['product_id'],
                quantity=quantity,
                amount=amount,
                unit_price=unit_price,
                purchase_price_at_sale=purchase_price_at_sale,
                profit=profit,
                sale_date=sale_date
            )
            
            db.session.add(sale)
            created_sales.append(sale)
        except Exception as e:
            errors.append(f'Qator {idx + 1}: {str(e)}')
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'{len(created_sales)} ta savdo muvaffaqiyatli qo\'shildi',
            'created_count': len(created_sales),
            'errors': errors if errors else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Xatolik yuz berdi: {str(e)}'}), 500
