"""
Token test skripti - token muammosini tekshirish uchun
"""
from app import create_app
from app.models import User
from flask_jwt_extended import create_access_token

app = create_app()

with app.app_context():
    # Admin foydalanuvchini topish
    admin = User.query.filter_by(role='admin').first()
    
    if not admin:
        print("❌ Admin foydalanuvchi topilmadi!")
        print("Iltimos, avval 'python create_admin.py' ni ishga tushiring.")
    else:
        print(f"✅ Admin topildi: {admin.username}")
        
        # Token yaratish
        token = create_access_token(identity=str(admin.id))
        print(f"✅ Token yaratildi: {token[:50]}...")
        print(f"\nToken uzunligi: {len(token)}")
        print(f"\nToken to'liq: {token}")

