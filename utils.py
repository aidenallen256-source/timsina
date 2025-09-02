import pandas as pd
from decimal import Decimal
from app import db
from models import Item
import os

def process_excel_file(file_path):
    """Process Excel file and import items"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Expected columns: sn, product, category, brand, cp, wholesale, sp, uom, opening_quantity
        required_columns = ['sn', 'product', 'category', 'brand', 'cp', 'wholesale', 'sp', 'uom', 'opening_quantity']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            return False, f"Missing columns: {', '.join(missing_cols)}"
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if item with this serial number already exists
                existing_item = Item.query.filter_by(sn=str(row['sn'])).first()
                
                if existing_item:
                    # Update existing item
                    existing_item.product = str(row['product'])
                    existing_item.category = str(row['category']) if pd.notna(row['category']) else ''
                    existing_item.brand = str(row['brand']) if pd.notna(row['brand']) else ''
                    existing_item.cp = Decimal(str(row['cp']))
                    existing_item.wholesale = Decimal(str(row['wholesale']))
                    existing_item.sp = Decimal(str(row['sp']))
                    existing_item.uom = str(row['uom'])
                    existing_item.opening_quantity = Decimal(str(row['opening_quantity']))
                    existing_item.current_quantity = Decimal(str(row['opening_quantity']))
                else:
                    # Create new item
                    new_item = Item(
                        sn=str(row['sn']),
                        product=str(row['product']),
                        category=str(row['category']) if pd.notna(row['category']) else '',
                        brand=str(row['brand']) if pd.notna(row['brand']) else '',
                        cp=Decimal(str(row['cp'])),
                        wholesale=Decimal(str(row['wholesale'])),
                        sp=Decimal(str(row['sp'])),
                        uom=str(row['uom']),
                        opening_quantity=Decimal(str(row['opening_quantity'])),
                        current_quantity=Decimal(str(row['opening_quantity']))
                    )
                    db.session.add(new_item)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")
        
        # Commit changes
        db.session.commit()
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if error_count > 0:
            return True, f"Processed {success_count} items successfully. {error_count} errors: {'; '.join(errors[:5])}"
        else:
            return True, f"Successfully imported {success_count} items"
            
    except Exception as e:
        db.session.rollback()
        return False, f"Error processing file: {str(e)}"

def generate_invoice_number(prefix="INV"):
    """Generate unique invoice number"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"

def calculate_tax_amount(amount, tax_rate):
    """Calculate tax amount"""
    return (Decimal(str(amount)) * Decimal(str(tax_rate))) / 100
