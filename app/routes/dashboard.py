from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Sale, Customer, Product, OnlineSale
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, ProgrammingError

dashboard_bp = Blueprint('dashboard', __name__)


def _to_float(v):
    """Decimal/None dan float ga — matematik aniqlik uchun"""
    if v is None:
        return 0.0
    return float(v)


def _to_int(v):
    """Decimal/None dan int ga"""
    if v is None:
        return 0
    return int(v)


def _default_stats():
    """DB xatoligida qaytariladigan standart javob"""
    return {
        'daily_sales': 0.0,
        'monthly_sales': 0.0,
        'yearly_sales': 0.0,
        'total_revenue': 0.0,
        'monthly_profit': 0.0,
        'total_profit': 0.0,
        'total_quantity_sold': 0,
        'total_quantity_sold_all_time': 0,
        'growth_percent': 0.0,
        'customers_count': 0,
        'products_count': 0,
        'error': 'Ulanish vaqtida xatolik. Sahifani yangilab qayta urinib ko\'ring.'
    }


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Dashboard statistikalarini qaytaradi — har bir ko'rsatkich alohida, matematikaga to'g'ri"""
    get_jwt_identity()
    today = datetime.now().date()
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)

    try:
        # Har biri alohida so'rov — sum(amount) va sum(quantity) bir xil jadvaldan, matematik jihatdan izchil
        daily_sales = _to_float(db.session.query(func.sum(Sale.amount)).filter(Sale.sale_date == today).scalar())
        monthly_sales = _to_float(db.session.query(func.sum(Sale.amount)).filter(
            Sale.sale_date >= this_month_start, Sale.sale_date <= today
        ).scalar())
        yearly_sales = _to_float(db.session.query(func.sum(Sale.amount)).filter(
            Sale.sale_date >= this_year_start, Sale.sale_date <= today
        ).scalar())
        total_revenue = _to_float(db.session.query(func.sum(Sale.amount)).scalar())

        total_quantity_sold = _to_int(db.session.query(func.sum(Sale.quantity)).filter(
            Sale.sale_date >= this_month_start, Sale.sale_date <= today
        ).scalar())
        total_quantity_sold_all_time = _to_int(db.session.query(func.sum(Sale.quantity)).scalar())

        last_month_sales = _to_float(db.session.query(func.sum(Sale.amount)).filter(
            Sale.sale_date >= last_month_start, Sale.sale_date <= last_month_end
        ).scalar())

        growth_percent = 0.0
        if last_month_sales > 0:
            growth_percent = ((monthly_sales - last_month_sales) / last_month_sales) * 100

        # Foyda: saqlangan profit bor bo'lsa shuni, yo'q bo'lsa amount - (tan narxi * miqdor)
        profit_expr = func.coalesce(Sale.profit, Sale.amount - (Product.purchase_price * Sale.quantity))
        monthly_profit = _to_float(db.session.query(func.sum(profit_expr)).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= this_month_start, Sale.sale_date <= today
        ).scalar())
        total_profit = _to_float(db.session.query(func.sum(profit_expr)).join(
            Product, Sale.product_id == Product.id
        ).scalar())

        customers_count = _to_int(db.session.query(func.count(Customer.id)).scalar())
        products_count = _to_int(db.session.query(func.count(Product.id)).filter(Product.status == 'active').scalar())

        return jsonify({
            'daily_sales': daily_sales,
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
            'total_revenue': total_revenue,
            'monthly_profit': monthly_profit,
            'total_profit': total_profit,
            'total_quantity_sold': total_quantity_sold,
            'total_quantity_sold_all_time': total_quantity_sold_all_time,
            'growth_percent': round(growth_percent, 2),
            'customers_count': customers_count,
            'products_count': products_count
        }), 200

    except OperationalError as e:
        db.session.rollback()
        print(f"[Dashboard /stats] OperationalError: {e}", flush=True)
        return jsonify({**_default_stats(), 'error': f'DB ulanish xatosi: {e}'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[Dashboard /stats] Xatolik: {type(e).__name__}: {e}", flush=True)
        return jsonify({**_default_stats(), 'error': str(e)}), 200

@dashboard_bp.route('/growth-dynamics', methods=['GET'])
@jwt_required()
def get_growth_dynamics():
    """O'sish dinamikasini qaytaradi (oxirgi 12 oy)"""
    try:
        today = datetime.now().date()
        data = []
        for i in range(11, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            if month_date.month == 12:
                month_end = month_date.replace(month=1, day=1, year=month_date.year + 1) - timedelta(days=1)
            else:
                month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
            sales = db.session.query(func.sum(Sale.amount)).filter(
                Sale.sale_date >= month_start,
                Sale.sale_date <= month_end
            ).scalar() or 0
            data.append({'month': month_date.strftime('%Y-%m'), 'sales': _to_float(sales)})
        return jsonify(data), 200
    except OperationalError:
        db.session.rollback()
        return jsonify([]), 200

@dashboard_bp.route('/top-products', methods=['GET'])
@jwt_required()
def get_top_products():
    """Eng ko'p sotilgan mahsulotlar — barcha vaqt bo'yicha"""
    try:
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.product_id == Product.id).group_by(
            Product.id, Product.name
        ).order_by(func.sum(Sale.quantity).desc()).limit(10).all()
        result = [{'id': p.id, 'name': p.name, 'total_quantity': _to_int(p.total_quantity), 'total_amount': _to_float(p.total_amount)} for p in top_products]
        return jsonify(result), 200
    except OperationalError:
        db.session.rollback()
        return jsonify([]), 200

@dashboard_bp.route('/top-customers', methods=['GET'])
@jwt_required()
def get_top_customers():
    """Eng ko'p xarid qilgan mijozlar — barcha vaqt bo'yicha"""
    try:
        top_customers = db.session.query(
            Customer.id,
            Customer.name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.customer_id == Customer.id).group_by(
            Customer.id, Customer.name
        ).order_by(func.sum(Sale.amount).desc()).limit(10).all()
        result = [{'id': c.id, 'name': c.name, 'total_quantity': _to_int(c.total_quantity), 'total_amount': _to_float(c.total_amount)} for c in top_customers]
        return jsonify(result), 200
    except OperationalError:
        db.session.rollback()
        return jsonify([]), 200

@dashboard_bp.route('/detailed-stats', methods=['GET'])
@jwt_required()
def get_detailed_stats():
    """Batafsil statistikalar — barcha vaqt bo'yicha (jami miqdor va summa)"""
    try:
        top_product = db.session.query(
            Product.name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.product_id == Product.id).group_by(
            Product.id, Product.name
        ).order_by(func.sum(Sale.quantity).desc()).first()

        top_customer = db.session.query(
            Customer.name,
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.customer_id == Customer.id).group_by(
            Customer.id, Customer.name
        ).order_by(func.sum(Sale.amount).desc()).first()

        total_sales_count = db.session.query(func.count(Sale.id)).scalar() or 0

        return jsonify({
            'top_product': {
                'name': top_product.name if top_product else 'Ma\'lumot yo\'q',
                'quantity': _to_int(top_product.total_quantity) if top_product else 0,
                'amount': _to_float(top_product.total_amount) if top_product else 0
            },
            'top_customer': {
                'name': top_customer.name if top_customer else 'Ma\'lumot yo\'q',
                'amount': _to_float(top_customer.total_amount) if top_customer else 0
            },
            'total_sales_count': _to_int(total_sales_count)
        }), 200
    except OperationalError:
        db.session.rollback()
        return jsonify({
            'top_product': {'name': 'Ma\'lumot yo\'q', 'quantity': 0, 'amount': 0},
            'top_customer': {'name': 'Ma\'lumot yo\'q', 'amount': 0},
            'total_sales_count': 0
        }), 200
