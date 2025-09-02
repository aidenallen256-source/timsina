# models.py (clean + fixed)
from datetime import datetime
from sqlalchemy import Numeric
from werkzeug.security import generate_password_hash, check_password_hash

# Remove circular import - db will be imported in app.py
# from app import db

# Global db reference that will be set later
db = None

def set_db(db_instance):
    """Set the database instance after models are imported"""
    global db
    db = db_instance

# ------------------------
# User Model
# ------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# ------------------------
# Customer Model
# ------------------------
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    balance = db.Column(Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------------
# Vendor Model
# ------------------------
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    balance = db.Column(Numeric(10, 2), default=0.00)
    tax_number = db.Column(db.String(50))
    discount_rate = db.Column(Numeric(5, 2), default=0.00)
    vat_rate = db.Column(Numeric(5, 2), default=0.00)
    excise_rate = db.Column(Numeric(5, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------------
# Item Model
# ------------------------
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(50), unique=True, nullable=False)
    product = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    cp = db.Column(Numeric(10, 2), nullable=False)  # Cost Price
    wholesale = db.Column(Numeric(10, 2), nullable=False)
    sp = db.Column(Numeric(10, 2), nullable=False)  # Selling Price
    uom = db.Column(db.String(20), nullable=False)  # Unit of Measure
    opening_quantity = db.Column(Numeric(10, 2), default=0.00)
    current_quantity = db.Column(Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def inc_quantity(self, qty):
        self.current_quantity = (self.current_quantity or 0) + (qty or 0)


# ------------------------
# Sale + Sale Items
# ------------------------
class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    subtotal_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    discount = db.Column(Numeric(10, 2), default=0.00)
    taxable_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_amount = db.Column(Numeric(10, 2), default=0.00)
    excise_amount = db.Column(Numeric(10, 2), default=0.00)
    total_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_enabled = db.Column(db.Boolean, default=False)
    excise_enabled = db.Column(db.Boolean, default=False)
    payment_type = db.Column(db.String(20), default='cash')  # cash, credit, bank
    payment_account = db.Column(db.String(100))
    sales_account = db.Column(db.String(100))
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    customer = db.relationship('Customer', backref='sales')
    items = db.relationship('SaleItem', backref='sale', cascade='all, delete-orphan')

    # Alias property for compatibility
    @property
    def invoice_number(self):
        return self.bill_number

    @invoice_number.setter
    def invoice_number(self, val):
        self.bill_number = val


class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    unit_price = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    total_price = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_enabled = db.Column(db.Boolean, default=False)
    excise_enabled = db.Column(db.Boolean, default=False)

    item = db.relationship('Item')


# ------------------------
# Purchase + Purchase Items
# ------------------------
class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    subtotal_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    discount = db.Column(Numeric(10, 2), default=0.00)
    taxable_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_amount = db.Column(Numeric(10, 2), default=0.00)
    excise_amount = db.Column(Numeric(10, 2), default=0.00)
    total_amount = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_enabled = db.Column(db.Boolean, default=False)
    excise_enabled = db.Column(db.Boolean, default=False)
    payment_type = db.Column(db.String(20), default='cash')
    payment_account = db.Column(db.String(100))
    purchase_account = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    vendor = db.relationship('Vendor', backref='purchases')
    items = db.relationship('PurchaseItem', backref='purchase', cascade='all, delete-orphan')

    @property
    def final_amount(self):
        return self.total_amount

    @final_amount.setter
    def final_amount(self, val):
        self.total_amount = val


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    unit_price = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    total_price = db.Column(Numeric(10, 2), default=0.00, nullable=False)
    vat_enabled = db.Column(db.Boolean, default=False)
    excise_enabled = db.Column(db.Boolean, default=False)

    item = db.relationship('Item')


# ------------------------
# Ledgers
# ------------------------
class PurchaseLedger(db.Model):
    __tablename__ = 'purchase_ledger'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    particular = db.Column(db.String(200), nullable=False)
    invoice_no = db.Column(db.String(50), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SalesLedger(db.Model):
    __tablename__ = 'sales_ledger'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    particular = db.Column(db.String(200), nullable=False)
    bill_no = db.Column(db.String(50), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------------
# Settings
# ------------------------
class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
