from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Sale, Product, Customer
from datetime import datetime, timedelta
from sqlalchemy import func
import os

ai_bp = Blueprint('ai', __name__)

# OpenAI API ni sozlash
openai_client = None
openai_api_key = os.getenv('OPENAI_API_KEY')

def init_openai_client():
    """OpenAI client'ni lazy initialization qilish"""
    global openai_client
    if openai_client is None and openai_api_key:
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=openai_api_key)
        except (ImportError, Exception) as e:
            print(f"⚠️  OpenAI sozlanmadi: {e}")
            openai_client = False  # False = sozlanmagan, None = hali tekshirilmagan

def get_business_context():
    """Biznes kontekstini yig'adi"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # Asosiy statistikalar
    total_sales = db.session.query(func.sum(Sale.amount)).filter(
        Sale.sale_date >= month_start
    ).scalar() or 0
    
    customers_count = Customer.query.count()
    products_count = Product.query.filter_by(status='active').count()
    
    # Eng ko'p sotilgan mahsulotlar
    top_products = db.session.query(
        Product.name,
        func.sum(Sale.quantity).label('quantity')
    ).select_from(Product).join(Sale, Product.id == Sale.product_id).filter(
        Sale.sale_date >= month_start
    ).group_by(Product.name).order_by(
        func.sum(Sale.quantity).desc()
    ).limit(5).all()
    
    # Eng ko'p xarid qilgan mijozlar
    top_customers = db.session.query(
        Customer.name,
        func.sum(Sale.amount).label('amount')
    ).select_from(Customer).join(Sale, Customer.id == Sale.customer_id).filter(
        Sale.sale_date >= month_start
    ).group_by(Customer.name).order_by(
        func.sum(Sale.amount).desc()
    ).limit(5).all()
    
    context = f"""
Nur & Garden Management System - Biznes ma'lumotlari:

Oylik savdo: {total_sales:,.0f} so'm
Mijozlar soni: {customers_count}
Mahsulotlar soni: {products_count}

Eng ko'p sotilgan mahsulotlar:
"""
    for product in top_products:
        context += f"- {product.name}: {product.quantity} dona\n"
    
    context += "\nEng ko'p xarid qilgan mijozlar:\n"
    for customer in top_customers:
        context += f"- {customer.name}: {customer.amount:,.0f} so'm\n"
    
    return context

@ai_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_ai():
    """AI ga savol berish"""
    user_id = int(get_jwt_identity())  # String'dan integer'ga o'zgartirish
    user = User.query.get(user_id)
    
    # Faqat admin uchun
    if user.role != 'admin':
        return jsonify({'error': 'Faqat admin foydalanishi mumkin'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('question'):
        return jsonify({'error': 'Savol kiritilishi shart'}), 400
    
    # OpenAI client'ni tekshirish
    if openai_client is None:
        init_openai_client()
    
    if not openai_client:
        return jsonify({'error': 'OpenAI API key sozlash shart. .env faylida OPENAI_API_KEY ni to\'ldiring.'}), 500
    
    try:
        # Biznes kontekstini olish
        context = get_business_context()
        
        # OpenAI API ga so'rov
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""Siz Nur & Garden Management System uchun biznes maslahatchisisiz. 
                    Quyidagi biznes ma'lumotlari bilan ishlaysiz:
                    
                    {context}
                    
                    Foydalanuvchilarga strategik maslahatlar bering, tahlil qiling va tavsiyalar bering.
                    Javoblaringiz o'zbek tilida bo'lsin."""
                },
                {
                    "role": "user",
                    "content": data['question']
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        return jsonify({
            'question': data['question'],
            'answer': answer
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'AI xatosi: {str(e)}'}), 500

@ai_bp.route('/report', methods=['POST'])
@jwt_required()
def generate_report():
    """AI yordamida hisobot yaratish"""
    user_id = int(get_jwt_identity())  # String'dan integer'ga o'zgartirish
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Faqat admin foydalanishi mumkin'}), 403
    
    data = request.get_json()
    report_type = data.get('type', 'monthly')  # monthly, quarterly
    
    # OpenAI client'ni tekshirish
    if openai_client is None:
        init_openai_client()
    
    if not openai_client:
        return jsonify({'error': 'OpenAI API key sozlash shart. .env faylida OPENAI_API_KEY ni to\'ldiring.'}), 500
    
    try:
        context = get_business_context()
        
        prompt = f"""
{context}

Yukoridagi ma'lumotlar asosida {report_type} hisobot yarating. 
Hisobot quyidagi bo'limlarni o'z ichiga olishi kerak:
1. Umumiy ko'rinish
2. Asosiy ko'rsatkichlar
3. Muvaffaqiyatlar
4. Muammolar va risklar
5. Tavsiyalar va keyingi qadamlar

Hisobot o'zbek tilida, professional va tahliliy bo'lsin.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Siz professional biznes hisobotlari yaratuvchi mutaxassissiz. Tahliliy va amaliy hisobotlar yarating."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        report = response.choices[0].message.content
        
        return jsonify({
            'type': report_type,
            'report': report,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Hisobot yaratishda xatolik: {str(e)}'}), 500

@ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """AI tavsiyalari (qisqa)"""
    user_id = int(get_jwt_identity())  # String'dan integer'ga o'zgartirish
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Faqat admin foydalanishi mumkin'}), 403
    
    # OpenAI client'ni tekshirish
    if openai_client is None:
        init_openai_client()
    
    if not openai_client:
        return jsonify({'error': 'OpenAI API key sozlash shart. .env faylida OPENAI_API_KEY ni to\'ldiring.'}), 500
    
    try:
        context = get_business_context()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Siz biznes maslahatchisisiz. Qisqa va amaliy tavsiyalar bering."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nYukoridagi ma'lumotlar asosida 3 ta qisqa va amaliy tavsiya bering. Javob o'zbek tilida bo'lsin."
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        recommendations = response.choices[0].message.content
        
        return jsonify({
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Tavsiyalar olishda xatolik: {str(e)}'}), 500

@ai_bp.route('/risks', methods=['GET'])
@jwt_required()
def get_risks():
    """AI xavflar tahlili"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Faqat admin foydalanishi mumkin'}), 403
    
    # OpenAI client'ni tekshirish
    if openai_client is None:
        init_openai_client()
    
    if not openai_client:
        return jsonify({'error': 'OpenAI API key sozlash shart. .env faylida OPENAI_API_KEY ni to\'ldiring.'}), 500
    
    try:
        context = get_business_context()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Siz biznes risk tahlilchisisiz. Xavflarni aniqlang va ularni kamaytirish bo'yicha tavsiyalar bering."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nYukoridagi ma'lumotlar asosida potensial xavflarni aniqlang va ularni kamaytirish bo'yicha tavsiyalar bering. Javob o'zbek tilida bo'lsin."
                }
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        risks = response.choices[0].message.content
        
        return jsonify({
            'risks': risks
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Xavflar tahlilida xatolik: {str(e)}'}), 500
