"""
Database yaratish skripti
Bu skript MySQL da database yaratadi va kerakli jadvallarni yaratadi.
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def create_database():
    """Database yaratadi"""
    # Database nomini olish
    db_name = os.getenv('DB_NAME', 'ngms_db')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    
    try:
        # Avval database bo'lmagan holda ulanish
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Database yaratish
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{db_name}' muvaffaqiyatli yaratildi yoki allaqachon mavjud")
        
        connection.close()
        
        # Endi Flask app ishga tushganda jadvallar yaratiladi
        print(f"✅ Database tayyor! Endi 'python run.py' ni ishga tushiring")
        
    except pymysql.Error as e:
        print(f"❌ Xatolik: {e}")
        print("\nTekshiring:")
        print("1. MySQL server ishlamoqda ekanligini")
        print("2. .env faylida database ma'lumotlari to'g'ri ekanligini")
        print("3. Foydalanuvchi paroli to'g'ri ekanligini")

if __name__ == '__main__':
    create_database()

