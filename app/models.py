from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin', nullable=False)  # admin, manager
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    package_type = db.Column(db.String(50), nullable=False)  # 250g, 500g, 1kg, 5kg, 10kg
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    margin_percent = db.Column(db.Numeric(5, 2))  # Avtomatik hisoblanadi
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_margin(self):
        if self.purchase_price and self.sale_price:
            margin = ((float(self.sale_price) - float(self.purchase_price)) / float(self.purchase_price)) * 100
            self.margin_percent = round(margin, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'package_type': self.package_type,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'margin_percent': float(self.margin_percent) if self.margin_percent else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    additional_name = db.Column(db.String(200))  # Qo'shimcha nomi (ixtiyoriy)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)  # Manzil
    latitude = db.Column(db.Numeric(10, 7))  # Mijoz koordinatalari (xarita uchun)
    longitude = db.Column(db.Numeric(10, 7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'additional_name': self.additional_name,
            'phone': self.phone,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Jami summa (savdo paytida qat'iy)
    unit_price = db.Column(db.Numeric(10, 2))  # Dona narxi savdo paytida (ixtiyoriy saqlanadi)
    purchase_price_at_sale = db.Column(db.Numeric(10, 2))  # Oldin tan narxi (savdo paytida) — kiritilsa sof foyda aniq bo'ladi
    profit = db.Column(db.Numeric(10, 2))  # Foyda: amount - (purchase_price_at_sale * quantity)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='sales')
    product = db.relationship('Product', backref='sales')
    
    def to_dict(self):
        amt = float(self.amount) if self.amount else None
        qty = self.quantity or 0
        unit_price = float(self.unit_price) if self.unit_price is not None else (round(amt / qty, 2) if qty and amt else None)
        purchase = float(self.purchase_price_at_sale) if self.purchase_price_at_sale is not None else (float(self.product.purchase_price) if self.product and self.product.purchase_price is not None else None)
        profit = float(self.profit) if self.profit is not None else (round(amt - (purchase or 0) * qty, 2) if amt is not None and qty else None)
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'amount': amt,
            'unit_price': unit_price,
            'purchase_price_at_sale': purchase,
            'profit': profit,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OnlineSale(db.Model):
    __tablename__ = 'online_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # uzum_market, yandex_market
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='online_sales')
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'amount': float(self.amount) if self.amount else None,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

