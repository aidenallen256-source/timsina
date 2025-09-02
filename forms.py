# forms.py (updated)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, SelectField, DecimalField, TextAreaField,
    IntegerField, DateTimeField, FieldList, FormField, BooleanField, DateField
)
from wtforms.validators import DataRequired, Email, Optional, NumberRange, ValidationError
from datetime import datetime
from decimal import Decimal

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    balance = DecimalField('Balance', validators=[Optional()], default=Decimal('0.00'))

class VendorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    balance = DecimalField('Balance', validators=[Optional()], default=Decimal('0.00'))
    tax_number = StringField('Tax Number', validators=[Optional()])
    discount_rate = DecimalField('Discount Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=Decimal('0.00'))
    vat_rate = DecimalField('VAT Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=Decimal('0.00'))
    excise_rate = DecimalField('Excise Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=Decimal('0.00'))

class ItemForm(FlaskForm):
    sn = StringField('Serial Number', validators=[DataRequired()])
    product = StringField('Product Name', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    brand = StringField('Brand', validators=[Optional()])
    cp = DecimalField('Cost Price', validators=[DataRequired(), NumberRange(min=0)])
    wholesale = DecimalField('Wholesale Price', validators=[DataRequired(), NumberRange(min=0)])
    sp = DecimalField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    uom = StringField('Unit of Measure', validators=[DataRequired()])
    opening_quantity = DecimalField('Opening Quantity', validators=[Optional(), NumberRange(min=0)], default=Decimal('0.00'))

class ExcelUploadForm(FlaskForm):
    file = FileField('Excel File', validators=[DataRequired(), FileAllowed(['xlsx', 'xls'], 'Excel files only!')])

class SaleItemForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    unit_price = DecimalField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    vat_enabled = BooleanField('VAT', default=False)
    excise_enabled = BooleanField('Excise', default=False)

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[Optional()])
    sale_date = DateField('Sale Date', validators=[DataRequired()], default=datetime.utcnow)
    discount = DecimalField('Discount', validators=[Optional(), NumberRange(min=0)], default=Decimal('0.00'))
    vat_enabled = BooleanField('VAT (13%)', default=False)
    excise_enabled = BooleanField('Excise', default=False)
    payment_type = SelectField('Payment Type', choices=[('cash', 'Cash'), ('credit', 'Credit'), ('bank', 'Bank')], default='cash')
    payment_account = StringField('Payment Account', validators=[Optional()])
    sales_account = StringField('Sales Account', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class PurchaseItemForm(FlaskForm):
    # Make item_id optional — user can choose an existing item OR enter new item details below
    item_id = SelectField('Item', coerce=int, validators=[Optional()], choices=[])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    unit_price = DecimalField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    vat_enabled = BooleanField('VAT', default=False)
    excise_enabled = BooleanField('Excise', default=False)

    # Inline fields to create a new item if item_id not selected
    product = StringField('Product Name', validators=[Optional()])
    category = StringField('Category', validators=[Optional()])
    brand = StringField('Brand', validators=[Optional()])
    cp = DecimalField('Cost Price', validators=[Optional(), NumberRange(min=0)])
    sp = DecimalField('Selling Price', validators=[Optional(), NumberRange(min=0)])
    uom = StringField('Unit of Measure', validators=[Optional()])
    opening_quantity = DecimalField('Opening Quantity', validators=[Optional(), NumberRange(min=0)], default=Decimal('0.00'))

    def validate(self):
        """
        Require either an existing item_id OR provided product name (for new item).
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        # If item_id not given, require product & cp & sp & uom
        if (not self.item_id.data) or (self.item_id.data == 0):
            missing = []
            if not self.product.data:
                missing.append('product')
            # we accept numeric 0 as valid cp/sp if explicit; handle None/empty string
            if self.cp.data is None:
                missing.append('cp')
            if self.sp.data is None:
                missing.append('sp')
            if not self.uom.data:
                missing.append('uom')
            if missing:
                self.product.errors.append('Provide product name, cost price (cp), selling price (sp) and uom when creating a new item.')
                return False

        return True

class QuickItemForm(FlaskForm):
    product = StringField('Product Name', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    cp = DecimalField('Cost Price', validators=[DataRequired(), NumberRange(min=0)])
    sp = DecimalField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    uom = StringField('Unit of Measure', validators=[DataRequired()])
    opening_quantity = DecimalField('Opening Quantity', validators=[Optional(), NumberRange(min=0)], default=Decimal('0.00'))

class SettingsForm(FlaskForm):
    vat_rate = DecimalField('VAT Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=Decimal('13.00'))
    excise_rate = DecimalField('Default Excise Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=Decimal('0.00'))
    company_name = StringField('Company Name', validators=[Optional()])
    company_address = TextAreaField('Company Address', validators=[Optional()])
    company_phone = StringField('Company Phone', validators=[Optional()])
    company_email = StringField('Company Email', validators=[Optional(), Email()])

class ReportFilterForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])

class PurchaseForm(FlaskForm):
    vendor_id = SelectField('Vendor', coerce=int, validators=[Optional()])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()], default=datetime.utcnow)
    invoice_number = StringField('Invoice Number', validators=[Optional()])
    discount = DecimalField('Discount', validators=[Optional(), NumberRange(min=0)], default=Decimal('0.00'))
    vat_enabled = BooleanField('VAT (13%)', default=False)
    excise_enabled = BooleanField('Excise', default=False)
    payment_type = SelectField('Payment Type', choices=[('cash', 'Cash'), ('credit', 'Credit'), ('bank', 'Bank')], default='cash')
    payment_account = StringField('Payment Account', validators=[Optional()])
    purchase_account = StringField('Purchase Account', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
