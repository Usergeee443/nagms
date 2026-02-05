"""
Bitta admin foydalanuvchi yaratish skripti
Bu skriptni faqat bir marta ishga tushiring.

Ishlatish:
    python3 create_admin.py                    # Interaktiv rejim
    python3 create_admin.py admin password123  # To'g'ridan-to'g'ri
"""
import sys
from app import create_app, db
from app.models import User

def create_admin(username=None, password=None, email=None, force=False):
    app = create_app()
    
    with app.app_context():
        # Agar admin allaqachon mavjud bo'lsa
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin and not force:
            print(f"⚠️  Admin allaqachon mavjud: {existing_admin.username}")
            if username and password:
                # Argumentlar orqali kelsa, avtomatik davom etadi
                print("Yangi admin yaratilmoqda...")
            else:
                response = input("Yangi admin yaratishni davom ettirasizmi? (ha/yoq): ").strip().lower()
                if response not in ['ha', 'yes', 'y', 'h']:
                    print("❌ Bekor qilindi.")
                    return
        
        # Yangi admin yaratish
        if not username:
            username = input("Admin username kiriting (default: admin): ").strip() or "admin"
        if not password:
            password = input("Kuchli parol kiriting (kamida 8 belgi): ").strip()
        
        if len(password) < 8:
            print("❌ Parol kamida 8 belgidan iborat bo'lishi kerak!")
            return
        
        if not email:
            email = input("Email kiriting (ixtiyoriy): ").strip() or f"{username}@ngms.com"
        
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin muvaffaqiyatli yaratildi!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Endi login sahifasiga kirib, bu ma'lumotlar bilan kirishingiz mumkin.")

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        # Argumentlar orqali
        username = sys.argv[1]
        password = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else None
        force = '--force' in sys.argv or '-f' in sys.argv
        create_admin(username, password, email, force=force)
    else:
        # Interaktiv rejim
        create_admin()

