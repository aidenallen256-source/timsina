import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "supersecretkey")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# -------------------------
# Configure the database
# -------------------------
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    # fallback for local dev
    db_url = "sqlite:///app.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization to avoid circular imports
with app.app_context():
    # Import models to ensure tables are created
    from models import User, Customer, Vendor, Item, Sale, SaleItem, Purchase, PurchaseItem, set_db  # noqa: F401
    # Set the db reference in models
    set_db(db)
    db.create_all()
    logging.info("Database tables created")

# -------------------------
# Import routes
# -------------------------
import routes  # noqa: E402

if __name__ == "__main__":
    app.run(debug=True)
