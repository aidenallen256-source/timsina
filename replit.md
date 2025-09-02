# Overview

This is a Flask-based accounting system designed for small to medium-sized businesses. The application provides comprehensive inventory management, sales tracking, purchase management, and customer/vendor relationship management. It features a web-based interface with Bootstrap styling, supports Excel file imports for bulk data entry, and generates professional invoices for transactions.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
The application uses Flask as the web framework with SQLAlchemy as the ORM for database operations. The architecture follows a traditional MVC pattern with clear separation of concerns:

- **Models** (`models.py`) - Database entities including User, Customer, Vendor, Item, Sale, Purchase, and their relationships
- **Routes** (`routes.py`) - HTTP endpoints handling business logic and request/response processing  
- **Forms** (`forms.py`) - WTForms for input validation and form rendering
- **Templates** - Jinja2 templates with Bootstrap 5 for responsive UI

## Database Design
Uses SQLAlchemy with a declarative base model approach. Key entities include:
- User management with password hashing
- Customer and Vendor management with balance tracking
- Item inventory with cost/wholesale/selling prices
- Sales and Purchase transactions with line items
- Numeric fields use precise decimal types for financial calculations

## Authentication & Security
Implements session-based authentication with a simple admin/admin login system. Uses Werkzeug for password hashing and includes CSRF protection via Flask-WTF. The application is configured for proxy deployment with ProxyFix middleware.

## File Handling
Supports Excel file uploads for bulk item imports using pandas for data processing. Files are handled securely with filename sanitization and size limits (16MB maximum).

## Frontend Architecture
Bootstrap 5-based responsive design with custom CSS styling. Uses Font Awesome for icons and Google Fonts for typography. JavaScript provides interactive features like dynamic form handling and sidebar navigation.

## Invoice Generation
Generates professional PDF-ready invoices for both sales and purchases with detailed line items, tax calculations, and company branding.

# External Dependencies

## Core Framework Dependencies
- **Flask** - Web application framework
- **SQLAlchemy & Flask-SQLAlchemy** - Database ORM
- **WTForms & Flask-WTF** - Form handling and validation
- **Werkzeug** - WSGI utilities and security helpers

## Data Processing
- **pandas** - Excel file processing for bulk imports
- **openpyxl** - Excel file format support

## Frontend Libraries (CDN)
- **Bootstrap 5** - CSS framework for responsive design
- **Font Awesome 6** - Icon library
- **Google Fonts (Inter)** - Typography

## Database
- Configured to use PostgreSQL via DATABASE_URL environment variable
- SQLAlchemy handles database abstraction allowing for multiple database backends

## Environment Configuration
- SESSION_SECRET - Flask session encryption key
- DATABASE_URL - Database connection string
- File upload directory configuration for item image/document storage