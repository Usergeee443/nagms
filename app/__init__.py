from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token muddati cheksiz (keyinchalik o'zgartiriladi)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Token faqat header'da
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ALGORITHM'] = 'HS256'
    # Flask-JWT-Extended 4.x uchun qo'shimcha sozlamalar
    app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']
    
    # Database Configuration (Render: DATABASE_URL, lokal: MySQL env)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render PostgreSQL: postgres:// -> postgresql:// (SQLAlchemy 1.4+)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:"
            f"{os.getenv('DB_PASSWORD', '')}@"
            f"{os.getenv('DB_HOST', 'localhost')}/"
            f"{os.getenv('DB_NAME', 'ngms_db')}"
        )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Ulanishni barqarorlashtirish: eski ulanishlarni tekshirish va qayta ishlatish
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,       # Har so'rovdan oldin ulanish tirikligini tekshirish
        'pool_recycle': 280,         # 280 sekunddan keyin ulanishni yangilash (MySQL timeout dan oldin)
        'pool_size': 5,
        'max_overflow': 10,
    }
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token muddati tugagan'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        import traceback
        print(f"Invalid token error: {error}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Noto\'g\'ri token: {str(error)}'}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token talab qilinadi'}), 401
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.customers import customers_bp
    from app.routes.sales import sales_bp
    from app.routes.ai import ai_bp
    from app.routes.test_auth import test_bp
    from app.routes.config import config_bp
    from app.routes.regions import regions_bp
    from app.routes.shops import shops_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(regions_bp, url_prefix='/api/regions')
    app.register_blueprint(shops_bp, url_prefix='/api/shops')
    
    # Serve frontend HTML files
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    @app.route('/<path:filename>')
    def serve_html(filename):
        if filename.endswith('.html'):
            return app.send_static_file(filename)
        # For other static files (CSS, JS, images), Flask will serve them automatically
        return app.send_static_file(filename)
    
    # Create tables (va MySQL da eski jadvallarga ustun qo'shish)
    with app.app_context():
        try:
            db.create_all()
            # Faqat MySQL uchun: sales jadvaliga ustunlar qo'shish (PostgreSQL da create_all yetadi)
            if not os.getenv('DATABASE_URL'):
                from sqlalchemy import text
                for col, definition in [
                    ('unit_price', 'DECIMAL(10, 2) NULL'),
                    ('purchase_price_at_sale', 'DECIMAL(10, 2) NULL'),
                    ('profit', 'DECIMAL(10, 2) NULL'),
                ]:
                    try:
                        r = db.session.execute(text("""
                            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sales' AND COLUMN_NAME = :name
                        """), {'name': col})
                        if r.scalar() is None:
                            db.session.execute(text(f"ALTER TABLE sales ADD COLUMN {col} {definition}"))
                            db.session.commit()
                            print(f"  ✅ sales.{col} qo'shildi")
                    except Exception as e:
                        db.session.rollback()
                        if 'Duplicate column' not in str(e):
                            print(f"  ⚠️  sales.{col}: {e}")
        except Exception as e:
            print(f"⚠️  Database xatosi: {e}")
            if os.getenv('DATABASE_URL'):
                print("   Render: DATABASE_URL tekshiring.")
            else:
                print("   Iltimos, avval database yarating:")
                print("   python create_database.py")
                print("   yoki MySQL da: CREATE DATABASE ngms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    return app

