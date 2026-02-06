from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Sale, Customer, Product, OnlineSale
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, ProgrammingError
from calendar import monthrange

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
        try:
            products_count = _to_int(db.session.query(func.count(Product.id)).filter(Product.status == 'active').scalar())
        except (OperationalError, ProgrammingError):
            products_count = _to_int(db.session.query(func.count(Product.id)).scalar())

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

def _month_start_end(year, month):
    """Berilgan yil-oy uchun oyning birinchi va oxirgi sanasi"""
    last_day = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, last_day)
    return start, end


@dashboard_bp.route('/growth-dynamics', methods=['GET'])
@jwt_required()
def get_growth_dynamics():
    """
    O'sish dinamikasini qaytaradi.
    Query: year=2026 — shu yilning 12 oyi (Yanvar–Dekabr);
           period=all — birinchi sotuvdan hozirgacha har oy.
    """
    try:
        today = datetime.now().date()
        period = request.args.get('period', '').strip().lower()
        year_param = request.args.get('year', '').strip()

        # Barcha davr: birinchi sotuvdan hozirgacha
        if period == 'all':
            first = db.session.query(func.min(Sale.sale_date)).scalar()
            if not first:
                return jsonify([]), 200
            if isinstance(first, datetime):
                first = first.date()
            start_year, start_month = first.year, first.month
            end_year, end_month = today.year, today.month
            data = []
            y, m = start_year, start_month
            while (y, m) <= (end_year, end_month):
                month_start, month_end = _month_start_end(y, m)
                sales = db.session.query(func.sum(Sale.amount)).filter(
                    Sale.sale_date >= month_start,
                    Sale.sale_date <= month_end
                ).scalar() or 0
                data.append({'month': f'{y}-{m:02d}', 'sales': _to_float(sales)})
                m += 1
                if m > 12:
                    m = 1
                    y += 1
            return jsonify(data), 200

        # Aniq yil: 12 oy
        if year_param.isdigit():
            y = int(year_param)
        else:
            y = today.year
        data = []
        for month in range(1, 13):
            month_start, month_end = _month_start_end(y, month)
            sales = db.session.query(func.sum(Sale.amount)).filter(
                Sale.sale_date >= month_start,
                Sale.sale_date <= month_end
            ).scalar() or 0
            data.append({'month': f'{y}-{month:02d}', 'sales': _to_float(sales)})
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


@dashboard_bp.route('/monthly-stats', methods=['GET'])
@jwt_required()
def get_monthly_stats():
    """
    Tanlangan oy uchun to'liq statistika.
    Query: year=2026&month=2
    """
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month or month < 1 or month > 12:
            return jsonify({'error': 'year va month parametrlari kerak (1-12)'}), 400
        
        month_start, month_end = _month_start_end(year, month)
        
        # Oy davomidagi jami savdo summasi
        total_sales = _to_float(db.session.query(func.sum(Sale.amount)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar())
        
        # Sotilgan mahsulotlar soni
        total_quantity = _to_int(db.session.query(func.sum(Sale.quantity)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar())
        
        # Savdolar soni
        sales_count = _to_int(db.session.query(func.count(Sale.id)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar())
        
        # Sof foyda
        profit_expr = func.coalesce(Sale.profit, Sale.amount - (Product.purchase_price * Sale.quantity))
        total_profit = _to_float(db.session.query(func.sum(profit_expr)).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar())
        
        # Top mahsulotlar (shu oyda)
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.product_id == Product.id).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).group_by(Product.id, Product.name).order_by(
            func.sum(Sale.quantity).desc()
        ).limit(10).all()
        
        # Top mijozlar (shu oyda)
        top_customers = db.session.query(
            Customer.id,
            Customer.name,
            Customer.additional_name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Sale.customer_id == Customer.id).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).group_by(Customer.id, Customer.name, Customer.additional_name).order_by(
            func.sum(Sale.amount).desc()
        ).limit(10).all()
        
        # Kunlik savdolar (grafik uchun)
        daily_sales = db.session.query(
            Sale.sale_date,
            func.sum(Sale.amount).label('amount'),
            func.sum(Sale.quantity).label('quantity')
        ).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).group_by(Sale.sale_date).order_by(Sale.sale_date).all()
        
        return jsonify({
            'year': year,
            'month': month,
            'total_sales': total_sales,
            'total_quantity': total_quantity,
            'sales_count': sales_count,
            'total_profit': total_profit,
            'top_products': [
                {'id': p.id, 'name': p.name, 'quantity': _to_int(p.total_quantity), 'amount': _to_float(p.total_amount)}
                for p in top_products
            ],
            'top_customers': [
                {'id': c.id, 'name': c.name, 'additional_name': c.additional_name, 'quantity': _to_int(c.total_quantity), 'amount': _to_float(c.total_amount)}
                for c in top_customers
            ],
            'daily_sales': [
                {'date': str(d.sale_date), 'amount': _to_float(d.amount), 'quantity': _to_int(d.quantity)}
                for d in daily_sales
            ]
        }), 200
        
    except OperationalError:
        db.session.rollback()
        return jsonify({'error': 'Ma\'lumotlar bazasi xatosi'}), 500
