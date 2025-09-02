import os
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Customer, Vendor, Item, Sale, SaleItem, Purchase, PurchaseItem
from forms import (LoginForm, CustomerForm, VendorForm, ItemForm, ExcelUploadForm,
                   SaleForm, PurchaseForm)
from utils import process_excel_file, generate_invoice_number
from sqlalchemy import func
from datetime import datetime
import uuid

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Simple authentication - admin/admin
        if username == 'admin' and password == 'admin':
            # Create admin user if doesn't exist
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User(username='admin')
                user.set_password('admin')
                db.session.add(user)
                db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    # Get dashboard statistics
    total_customers = Customer.query.count()
    total_vendors = Vendor.query.count()
    total_items = Item.query.count()
    total_sales = Sale.query.count()
    total_purchases = Purchase.query.count()
    
    # Get recent sales
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
    recent_purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).limit(5).all()
    
    # Get low stock items (items with current_quantity < 10)
    low_stock_items = Item.query.filter(Item.current_quantity < 10).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_customers=total_customers,
                         total_vendors=total_vendors,
                         total_items=total_items,
                         total_sales=total_sales,
                         total_purchases=total_purchases,
                         recent_sales=recent_sales,
                         recent_purchases=recent_purchases,
                         low_stock_items=low_stock_items)

# Customer routes
@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            balance=form.balance.data or Decimal('0.00')
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html', form=form, title='Add Customer')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.balance = form.balance.data or Decimal('0.00')
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html', form=form, title='Edit Customer')

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))

# Vendor routes
@app.route('/vendors')
@login_required
def vendors():
    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@app.route('/vendors/add', methods=['GET', 'POST'])
@login_required
def add_vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            balance=form.balance.data or Decimal('0.00'),
            tax_number=form.tax_number.data,
            discount_rate=form.discount_rate.data or Decimal('0.00'),
            vat_rate=form.vat_rate.data or Decimal('0.00'),
            excise_rate=form.excise_rate.data or Decimal('0.00')
        )
        db.session.add(vendor)
        db.session.commit()
        flash('Vendor added successfully!', 'success')
        return redirect(url_for('vendors'))
    
    return render_template('vendor_form.html', form=form, title='Add Vendor')

@app.route('/vendors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    form = VendorForm(obj=vendor)
    
    if form.validate_on_submit():
        vendor.name = form.name.data
        vendor.email = form.email.data
        vendor.phone = form.phone.data
        vendor.address = form.address.data
        vendor.balance = form.balance.data or Decimal('0.00')
        vendor.tax_number = form.tax_number.data
        vendor.discount_rate = form.discount_rate.data or Decimal('0.00')
        vendor.vat_rate = form.vat_rate.data or Decimal('0.00')
        vendor.excise_rate = form.excise_rate.data or Decimal('0.00')
        db.session.commit()
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('vendors'))
    
    return render_template('vendor_form.html', form=form, title='Edit Vendor')

@app.route('/vendors/delete/<int:id>')
@login_required
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    flash('Vendor deleted successfully!', 'success')
    return redirect(url_for('vendors'))

# Item routes
@app.route('/items')
@login_required
def items():
    items = Item.query.all()
    return render_template('items.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(
            sn=form.sn.data,
            product=form.product.data,
            category=form.category.data,
            brand=form.brand.data,
            cp=form.cp.data,
            wholesale=form.wholesale.data,
            sp=form.sp.data,
            uom=form.uom.data,
            opening_quantity=form.opening_quantity.data or Decimal('0.00'),
            current_quantity=form.opening_quantity.data or Decimal('0.00')
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('items'))
    
    return render_template('item_form.html', form=form, title='Add Item')

@app.route('/items/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    form = ItemForm(obj=item)
    
    if form.validate_on_submit():
        item.sn = form.sn.data
        item.product = form.product.data
        item.category = form.category.data
        item.brand = form.brand.data
        item.cp = form.cp.data
        item.wholesale = form.wholesale.data
        item.sp = form.sp.data
        item.uom = form.uom.data
        item.opening_quantity = form.opening_quantity.data or Decimal('0.00')
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('items'))
    
    return render_template('item_form.html', form=form, title='Edit Item')

@app.route('/items/delete/<int:id>')
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('items'))

@app.route('/items/import', methods=['GET', 'POST'])
@login_required
def import_items():
    form = ExcelUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(file_path)
            
            # Process the Excel file
            success, message = process_excel_file(file_path)
            
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            
            return redirect(url_for('items'))
    
    return render_template('item_form.html', form=form, title='Import Items from Excel', is_import=True)

# Sales routes
@app.route('/sales')
@login_required
def sales():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', sales=sales)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    customers = Customer.query.all()
    # only items with stock > 0 for sale selection
    items = Item.query.filter(Item.current_quantity > 0).all()
    
    if request.method == 'POST':
        try:
            # Debug logging for request data
            app.logger.info("Processing sale creation request")
            app.logger.info(f"Form data keys: {list(request.form.keys())}")
            app.logger.info(f"Files: {list(request.files.keys()) if request.files else 'No files'}")
            
            customer_id = request.form.get('customer_id')
            discount = Decimal(request.form.get('discount', '0') or '0')
            notes = request.form.get('notes', '')
            vat_enabled = request.form.get('vat_enabled') == 'on'
            excise_enabled = request.form.get('excise_enabled') == 'on'
            
            # Log the extracted values
            app.logger.info(f"Extracted values: customer_id={customer_id}, discount={discount}, vat_enabled={vat_enabled}, excise_enabled={excise_enabled}")
            
            # Get sale items from form arrays
            item_ids = request.form.getlist('item_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            app.logger.info(f"Item arrays: item_ids={item_ids}, quantities={quantities}, unit_prices={unit_prices}")
            
            if not item_ids:
                flash('Please add at least one item to the sale', 'error')
                return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')
            
            # Calculate subtotal and prepare sale items
            subtotal = Decimal('0.00')
            sale_items_data = []
            for i in range(len(item_ids)):
                raw_item_id = item_ids[i]
                raw_qty = quantities[i] if i < len(quantities) else '0'
                raw_up = unit_prices[i] if i < len(unit_prices) else '0'
                if not raw_item_id:
                    flash('Select an item for sale or provide valid item id', 'error')
                    return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')
                item_id = int(raw_item_id)
                try:
                    quantity = Decimal(raw_qty)
                    unit_price = Decimal(raw_up)
                except (InvalidOperation, TypeError):
                    flash('Invalid quantity or unit price', 'error')
                    return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')
                
                item = Item.query.get(item_id)
                if not item:
                    flash('Selected item not found', 'error')
                    return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')
                if item.current_quantity < quantity:
                    flash(f'Insufficient stock for {item.product}. Available: {item.current_quantity}', 'error')
                    return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')
                
                total_price = (quantity * unit_price)
                subtotal += total_price
                sale_items_data.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price
                })
            
            taxable_amount = subtotal - discount
            if taxable_amount < 0:
                taxable_amount = Decimal('0.00')
            
            # VAT 13% if enabled
            vat_amount = (taxable_amount * Decimal('13.00') / Decimal('100.00')) if vat_enabled else Decimal('0.00')
            # Excise: for sales we can check settings or assume 0 (leave as 0 unless you have specific excise logic)
            excise_amount = Decimal('0.00')
            
            total_amount = taxable_amount + vat_amount + excise_amount
            
            # Create Sale: use bill_number (model expects bill_number, not invoice_number)
            bill_no = generate_invoice_number("SALE")
            sale = Sale(
                bill_number=bill_no,
                customer_id=int(customer_id) if customer_id else None,
                subtotal_amount=subtotal,
                discount=discount,
                taxable_amount=taxable_amount,
                vat_amount=vat_amount,
                excise_amount=excise_amount,
                total_amount=total_amount,
                vat_enabled=vat_enabled,
                excise_enabled=excise_enabled
            )
            if notes:
                sale.notes = notes
            
            db.session.add(sale)
            db.session.flush()  # to get sale.id
            
            # Add sale items and reduce inventory
            for sd in sale_items_data:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    item_id=sd['item_id'],
                    quantity=sd['quantity'],
                    unit_price=sd['unit_price'],
                    total_price=sd['total_price'],
                    vat_enabled=vat_enabled,
                    excise_enabled=False
                )
                db.session.add(sale_item)
                # decrement stock
                item = Item.query.get(sd['item_id'])
                item.current_quantity = (item.current_quantity or Decimal('0.00')) - sd['quantity']
            
            db.session.commit()
            flash('Sale created successfully!', 'success')
            return redirect(url_for('sales'))
        except Exception as e:
            db.session.rollback()
            app.logger.exception("Error creating sale")
            # Enhanced error logging
            app.logger.error(f"Sale creation failed with error: {str(e)}")
            app.logger.error(f"Form data: customer_id={customer_id}, discount={discount}, notes={notes}")
            app.logger.error(f"Item data: {sale_items_data}")
            app.logger.error(f"Exception type: {type(e).__name__}")
            flash(f'Error creating sale: {str(e)}', 'error')
    
    return render_template('sales_form.html', customers=customers, items=items, title='Add Sale')

@app.route('/sales/view/<int:id>')
@login_required
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('invoice.html', sale=sale, title='Sale Invoice')

@app.route('/sales/delete/<int:id>')
@login_required
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    
    # Restore inventory quantities
    for sale_item in sale.items:
        item = Item.query.get(sale_item.item_id)
        item.current_quantity = (item.current_quantity or Decimal('0.00')) + sale_item.quantity
    
    db.session.delete(sale)
    db.session.commit()
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('sales'))

# Purchase routes
@app.route('/purchases')
@login_required
def purchases():
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return render_template('purchases.html', purchases=purchases)

@app.route('/purchases/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    vendors = Vendor.query.all()
    items = Item.query.all()
    
    if request.method == 'POST':
        try:
            vendor_id = request.form.get('vendor_id')
            discount = Decimal(request.form.get('discount', '0') or '0')
            notes = request.form.get('notes', '')
            vat_enabled = request.form.get('vat_enabled') == 'on'
            excise_enabled = request.form.get('excise_enabled') == 'on'
            
            # arrays from front-end (existing item_id[] or empty if new item)
            item_ids = request.form.getlist('item_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            # optional arrays for new-item metadata (if you provide them in template)
            products = request.form.getlist('product[]')        # product[] (optional)
            categories = request.form.getlist('category[]')    # category[]
            brands = request.form.getlist('brand[]')           # brand[]
            cps = request.form.getlist('cp[]')                 # cost price (optional)
            sps = request.form.getlist('sp[]')                 # selling price (optional)
            uoms = request.form.getlist('uom[]')               # uom[]
            
            if not item_ids:
                flash('Please add at least one item to the purchase', 'error')
                return render_template('purchase_form.html', vendors=vendors, items=items, title='Add Purchase')
            
            # Build purchase item list, allowing creation of new items if item_id empty
            purchase_items_data = []
            subtotal = Decimal('0.00')
            for i in range(len(item_ids)):
                raw_item_id = item_ids[i]
                raw_qty = quantities[i] if i < len(quantities) else '0'
                raw_up = unit_prices[i] if i < len(unit_prices) else '0'
                try:
                    quantity = Decimal(raw_qty)
                    unit_price = Decimal(raw_up)
                except (InvalidOperation, TypeError):
                    flash('Invalid quantity or unit price entered', 'error')
                    return render_template('purchase_form.html', vendors=vendors, items=items, title='Add Purchase')
                
                product_name = products[i] if i < len(products) else ''
                category = categories[i] if i < len(categories) else ''
                brand = brands[i] if i < len(brands) else ''
                cp_val = None
                sp_val = None
                if i < len(cps) and cps[i]:
                    try:
                        cp_val = Decimal(cps[i])
                    except:
                        cp_val = None
                if i < len(sps) and sps[i]:
                    try:
                        sp_val = Decimal(sps[i])
                    except:
                        sp_val = None
                uom = uoms[i] if i < len(uoms) and uoms[i] else 'pcs'
                
                total_price = (unit_price * quantity)
                subtotal += total_price
                
                purchase_items_data.append({
                    'item_id': int(raw_item_id) if raw_item_id else None,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'product': product_name,
                    'category': category,
                    'brand': brand,
                    'cp': cp_val if cp_val is not None else unit_price,
                    'sp': sp_val if sp_val is not None else unit_price,
                    'uom': uom
                })
            
            taxable_amount = subtotal - discount
            if taxable_amount < 0:
                taxable_amount = Decimal('0.00')
            
            # VAT 13% if enabled
            vat_amount = (taxable_amount * Decimal('13.00') / Decimal('100.00')) if vat_enabled else Decimal('0.00')
            
            # Excise: use vendor.excise_rate (if toggled on and vendor specified), else 0
            excise_amount = Decimal('0.00')
            if excise_enabled and vendor_id:
                vendor_obj = Vendor.query.get(int(vendor_id))
                if vendor_obj and vendor_obj.excise_rate:
                    excise_rate = Decimal(str(vendor_obj.excise_rate))
                    excise_amount = (taxable_amount * excise_rate / Decimal('100.00'))
            
            total_amount = taxable_amount + vat_amount + excise_amount
            
            # Invoice number: either posted or auto-generated
            invoice_no = request.form.get('invoice_number') or generate_invoice_number("PUR")
            
            purchase = Purchase(
                invoice_number=invoice_no,
                vendor_id=int(vendor_id) if vendor_id else None,
                subtotal_amount=subtotal,
                discount=discount,
                taxable_amount=taxable_amount,
                vat_amount=vat_amount,
                excise_amount=excise_amount,
                total_amount=total_amount,
                vat_enabled=vat_enabled,
                excise_enabled=excise_enabled
            )
            if notes:
                purchase.notes = notes
            
            db.session.add(purchase)
            db.session.flush()  # get purchase.id
            
            # For each purchase item: either use existing item or create a new item
            for pid in purchase_items_data:
                item_obj = None
                if pid['item_id']:
                    item_obj = Item.query.get(pid['item_id'])
                
                if not item_obj:
                    # create new item
                    sn = f"SN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:5].upper()}"
                    item_obj = Item(
                        sn=sn,
                        product=pid.get('product') or 'Unnamed Item',
                        category=pid.get('category') or '',
                        brand=pid.get('brand') or '',
                        cp=pid.get('cp') or pid.get('unit_price') or Decimal('0.00'),
                        wholesale=pid.get('cp') or pid.get('unit_price') or Decimal('0.00'),
                        sp=pid.get('sp') or pid.get('unit_price') or Decimal('0.00'),
                        uom=pid.get('uom') or 'pcs',
                        opening_quantity=pid.get('quantity') or Decimal('0.00'),
                        current_quantity=pid.get('quantity') or Decimal('0.00')
                    )
                    db.session.add(item_obj)
                    db.session.flush()  # get item_obj.id
            
                # create PurchaseItem
                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    item_id=item_obj.id,
                    quantity=pid['quantity'],
                    unit_price=pid['unit_price'],
                    total_price=pid['total_price'],
                    vat_enabled=vat_enabled,
                    excise_enabled=excise_enabled
                )
                db.session.add(purchase_item)
                
                # update item current_quantity
                item_obj.current_quantity = (item_obj.current_quantity or Decimal('0.00')) + pid['quantity']
            
            db.session.commit()
            flash('Purchase created successfully!', 'success')
            return redirect(url_for('purchases'))
        except Exception as e:
            db.session.rollback()
            app.logger.exception("Error creating purchase")
            flash(f'Error creating purchase: {str(e)}', 'error')
    
    return render_template('purchase_form.html', vendors=vendors, items=items, title='Add Purchase')

@app.route('/purchases/view/<int:id>')
@login_required
def view_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    return render_template('invoice.html', purchase=purchase, title='Purchase Invoice')

@app.route('/purchases/delete/<int:id>')
@login_required
def delete_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    
    # Restore inventory quantities (subtract the purchase quantity)
    for purchase_item in purchase.items:
        item = Item.query.get(purchase_item.item_id)
        item.current_quantity = (item.current_quantity or Decimal('0.00')) - purchase_item.quantity
    
    db.session.delete(purchase)
    db.session.commit()
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('purchases'))

# API routes for dynamic data
@app.route('/api/item/<int:id>')
@login_required
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({
        'id': item.id,
        'product': item.product,
        'sp': float(item.sp),
        'current_quantity': float(item.current_quantity),
        'uom': item.uom
    })
