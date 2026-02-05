"""
Database migratsiya skripti
Bu skript quyidagi o'zgarishlarni bajaradi:
1. shops jadvalini customers ga o'zgartirish
2. sales jadvalidagi shop_id ni customer_id ga o'zgartirish
3. sales jadvalidagi sale_type ustunini o'chirish yoki standart qiymat berish
4. Yangi ustunlar qo'shish (agar kerak bo'lsa)
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def migrate_database():
    """Database migratsiyasini bajaradi"""
    db_name = os.getenv('DB_NAME', 'ngms_db')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            print("🔄 Database migratsiyasi boshlandi...")
            
            # 1. shops jadvalini customers ga o'zgartirish
            print("\n📋 Shops jadvalini customers ga o'zgartiryapman...")
            try:
                # Avval customers jadvali mavjudligini tekshirish
                cursor.execute("SHOW TABLES LIKE 'customers'")
                customers_exists = cursor.fetchone()
                
                if not customers_exists:
                    # shops jadvalini customers ga rename qilish
                    cursor.execute("RENAME TABLE shops TO customers")
                    print("  ✅ shops jadvali customers ga o'zgartirildi")
                else:
                    print("  ℹ️  customers jadvali allaqachon mavjud")
            except pymysql.err.OperationalError as e:
                if "doesn't exist" in str(e):
                    print("  ℹ️  shops jadvali mavjud emas, customers jadvali allaqachon mavjud bo'lishi mumkin")
                else:
                    print(f"  ⚠️  Xatolik: {e}")
            
            # 2. sales jadvalidagi shop_id ni customer_id ga o'zgartirish
            print("\n📋 Sales jadvalidagi shop_id ni customer_id ga o'zgartiryapman...")
            try:
                # Avval shop_id ustuni mavjudligini tekshirish
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'sales' 
                    AND COLUMN_NAME = 'shop_id'
                """, (db_name,))
                shop_id_exists = cursor.fetchone()
                
                if shop_id_exists:
                    # Foreign key constraint nomini topish
                    cursor.execute("""
                        SELECT CONSTRAINT_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_SCHEMA = %s 
                        AND TABLE_NAME = 'sales' 
                        AND COLUMN_NAME = 'shop_id'
                        AND REFERENCED_TABLE_NAME IS NOT NULL
                    """, (db_name,))
                    fk_constraint = cursor.fetchone()
                    
                    if fk_constraint:
                        # Foreign key constraint ni o'chirish
                        cursor.execute(f"ALTER TABLE sales DROP FOREIGN KEY {fk_constraint[0]}")
                        print(f"  ✅ Foreign key constraint {fk_constraint[0]} o'chirildi")
                    
                    # shop_id ustunini customer_id ga o'zgartirish
                    cursor.execute("""
                        ALTER TABLE sales 
                        CHANGE COLUMN shop_id customer_id INT NOT NULL
                    """)
                    print("  ✅ shop_id ustuni customer_id ga o'zgartirildi")
                    
                    # Yangi foreign key constraint qo'shish
                    try:
                        cursor.execute("""
                            ALTER TABLE sales 
                            ADD CONSTRAINT fk_sales_customer 
                            FOREIGN KEY (customer_id) REFERENCES customers(id)
                        """)
                        print("  ✅ Yangi foreign key constraint qo'shildi")
                    except pymysql.err.OperationalError as e:
                        if "Duplicate" in str(e):
                            print("  ℹ️  Foreign key constraint allaqachon mavjud")
                        else:
                            print(f"  ⚠️  Xatolik: {e}")
                else:
                    # customer_id mavjudligini tekshirish
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = %s 
                        AND TABLE_NAME = 'sales' 
                        AND COLUMN_NAME = 'customer_id'
                    """, (db_name,))
                    customer_id_exists = cursor.fetchone()
                    
                    if customer_id_exists:
                        print("  ℹ️  customer_id allaqachon mavjud")
                    else:
                        # customer_id ustunini qo'shish
                        print("  ⚠️  shop_id ham customer_id ham mavjud emas, customer_id qo'shilmoqda...")
                        cursor.execute("""
                            ALTER TABLE sales 
                            ADD COLUMN customer_id INT NOT NULL DEFAULT 1
                        """)
                        print("  ✅ customer_id ustuni qo'shildi")
                        
                        # Foreign key constraint qo'shish
                        try:
                            cursor.execute("""
                                ALTER TABLE sales 
                                ADD CONSTRAINT fk_sales_customer 
                                FOREIGN KEY (customer_id) REFERENCES customers(id)
                            """)
                            print("  ✅ Foreign key constraint qo'shildi")
                        except pymysql.err.OperationalError as e:
                            print(f"  ⚠️  Foreign key constraint qo'shishda xatolik: {e}")
                            
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e) or "Unknown column" in str(e):
                    print("  ℹ️  customer_id allaqachon mavjud yoki shop_id mavjud emas")
                else:
                    print(f"  ⚠️  Xatolik: {e}")
            
            # 3. sales jadvalidagi sale_type ustunini tekshirish va o'chirish
            print("\n📋 Sales jadvalidagi sale_type ustunini tekshiryapman...")
            try:
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'sales' 
                    AND COLUMN_NAME = 'sale_type'
                """, (db_name,))
                sale_type_exists = cursor.fetchone()
                
                if sale_type_exists:
                    # sale_type ustunini o'chirish (chunki modelda yo'q)
                    cursor.execute("""
                        ALTER TABLE sales DROP COLUMN sale_type
                    """)
                    print("  ✅ sale_type ustuni o'chirildi")
                else:
                    print("  ℹ️  sale_type ustuni mavjud emas")
            except pymysql.err.OperationalError as e:
                print(f"  ⚠️  sale_type ustunini o'chirishda xatolik: {e}")
            
            # 3.1. sales jadvaliga savdo paytidagi narx va foyda ustunlari (mahsulot narxi o'zgasa ham eski savdolar o'zgarmaydi)
            print("\n📋 Sales jadvaliga unit_price, purchase_price_at_sale, profit qo'shilmoqda...")
            for col_name, col_def in [
                ('unit_price', 'DECIMAL(10, 2) NULL COMMENT "Dona narxi savdo paytida"'),
                ('purchase_price_at_sale', 'DECIMAL(10, 2) NULL COMMENT "Xarid narxi savdo paytida"'),
                ('profit', 'DECIMAL(10, 2) NULL COMMENT "Foyda"'),
            ]:
                try:
                    cursor.execute(f"""
                        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'sales' AND COLUMN_NAME = %s
                    """, (db_name, col_name))
                    if not cursor.fetchone():
                        cursor.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_def}")
                        print(f"  ✅ sales.{col_name} qo'shildi")
                    else:
                        print(f"  ℹ️  sales.{col_name} allaqachon mavjud")
                except pymysql.err.OperationalError as e:
                    print(f"  ⚠️  {col_name}: {e}")
            
            # 4. customers jadvali ustunlarini yangilash
            print("\n📋 Customers jadvali ustunlarini tekshiryapman...")
            
            # address ustunini qo'shish
            try:
                cursor.execute("""
                    ALTER TABLE customers 
                    ADD COLUMN address TEXT NULL
                """)
                print("  ✅ customers.address qo'shildi")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("  ℹ️  customers.address allaqachon mavjud")
                else:
                    print(f"  ⚠️  Xatolik: {e}")
            
            # latitude va longitude ustunlarini qo'shish (agar yo'q bo'lsa)
            try:
                cursor.execute("""
                    ALTER TABLE customers 
                    ADD COLUMN latitude DECIMAL(10, 7) NULL
                """)
                print("  ✅ customers.latitude qo'shildi")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("  ℹ️  customers.latitude allaqachon mavjud")
                else:
                    print(f"  ⚠️  Xatolik: {e}")
            
            try:
                cursor.execute("""
                    ALTER TABLE customers 
                    ADD COLUMN longitude DECIMAL(10, 7) NULL
                """)
                print("  ✅ customers.longitude qo'shildi")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("  ℹ️  customers.longitude allaqachon mavjud")
                else:
                    print(f"  ⚠️  Xatolik: {e}")
            
            # 5. Sales jadvali strukturasini ko'rsatish
            print("\n📋 Joriy sales jadvali strukturasi:")
            cursor.execute(f"DESCRIBE sales")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'} {col[3] or ''} {col[4] or ''}")
            
            connection.commit()
            print("\n✅ Migratsiya muvaffaqiyatli yakunlandi!")
            print("✅ Endi ilovani qayta ishga tushirishingiz mumkin.")
        
        connection.close()
        
    except pymysql.Error as e:
        print(f"❌ Xatolik: {e}")
        print("\nTekshiring:")
        print("1. MySQL server ishlamoqda ekanligini")
        print("2. .env faylida database ma'lumotlari to'g'ri ekanligini")
        print("3. Database mavjud ekanligini")

if __name__ == '__main__':
    migrate_database()

