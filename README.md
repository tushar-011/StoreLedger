# 🧾 StoreLedger

> **A Billing, Inventory, Customer, Supplier, Wallet, Reporting, and Database Management System built with Flask and MySQL.**

StoreLedger is a college mini-project designed to demonstrate practical database concepts through a real-world store management application. It combines a web-based interface with MySQL stored programming features such as **procedures, functions, triggers, views, transactions, locking, error handling, and audit logging**.

---

## ✨ Highlights

- 🛒 Product and inventory management
- 🧾 Billing and invoice generation
- 👥 Customer management
- 💰 Customer wallet and reward points
- 🚚 Supplier management
- 📦 Restocking and low-stock tracking
- ⏳ Expiry management
- 📊 Sales and category-wise reports
- 🔐 Login, logout, sessions, and password hashing
- 🧠 MySQL procedures, functions, triggers, and views
- 🧾 Audit logging
- 🌙 Dark mode
- 📱 Responsive interface
- ▶️ One-click Windows launcher using a `.bat` file

---

# 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Database Concepts Demonstrated](#-database-concepts-demonstrated)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [Using the BAT Launcher](#%EF%B8%8F-using-the-bat-launcher)
- [Login](#-login)
- [Major Application Modules](#-major-application-modules)
- [Important Database Objects](#-important-database-objects)
- [Testing](#-testing)
- [Security Notes](#-security-notes)
- [Future Improvements](#-future-improvements)
- [GitHub Setup](#-github-setup)
- [Project Status](#-project-status)

---

# 📖 About the Project

**StoreLedger** is a full-stack store management application developed as a DBMS mini-project.

The application allows a store to manage:

- Products
- Categories
- Inventory
- Customers
- Suppliers
- Billing
- Wallet payments
- Reward points
- Expiry dates
- Sales reports
- Audit logs

The project was also designed to demonstrate database-side logic instead of keeping all business logic inside Python.

---

# 🚀 Features

## 📦 Product Management

StoreLedger includes complete product CRUD functionality.

### Available operations

- Add products
- Edit products
- Delete products
- Search products
- Assign a category
- Assign a supplier
- Set product price
- Set stock quantity
- Set minimum stock
- Set tax rate
- Set expiry date
- Highlight low-stock products
- Display supplier information
- Prevent expired products from being billed

---

## 🗂️ Category Management

The application includes complete category CRUD functionality.

### Features

- View all categories
- Add a category
- Edit a category
- Delete unused categories
- Prevent deletion of categories currently assigned to products
- Show number of products in each category
- Generate category-wise reports

---

## 📊 Category-wise Reports

Category reports include:

- Category name
- Number of products
- Total stock units
- Inventory value
- Units sold
- Sales revenue

---

## 📦 Inventory Management

The Inventory module provides a central view of product stock.

### Features

- Total product count
- Total stock units
- Low-stock product count
- Out-of-stock product count
- Product stock status
- Minimum-stock monitoring
- Restock products
- Supplier information
- Low-stock page
- Expiry management page

---

## ⚠️ Low Stock Management

Products are automatically identified as low stock when:

```text
stock <= minimum_stock
```

Low-stock products are visually highlighted in the application.

A dedicated MySQL view is also used for low-stock reporting.

---

## ⏳ Expiry Management

Products can contain expiry dates.

### Expiry statuses

- Expired
- Critical
- Expiring Soon
- Safe

The application:

- Shows expiry alerts
- Provides a dedicated expiry page
- Prevents expired products from appearing in billing
- Performs backend expiry validation before completing an order

---

## 🚚 Supplier Management

StoreLedger supports supplier CRUD and supplier-product relationships.

### Features

- Add supplier
- Edit supplier
- Delete supplier
- View suppliers
- Store supplier contact information
- Link products to suppliers
- Display suppliers on Product pages
- Display suppliers in Inventory
- Display supplier information during restocking

---

## 👥 Customer Management

The Customer module supports:

- Add customer
- Edit customer
- Delete customer
- Search customers
- Customer details page
- Purchase history
- Wallet balance
- Reward points
- Wallet transaction history

Walk-in billing is also supported without requiring a customer account.

---

## 💰 Customer Wallet

Customers can maintain a StoreLedger wallet.

### Wallet features

- Add wallet balance
- Pay using wallet
- Wallet transaction history
- Wallet balance validation
- Automatic wallet deduction
- Insufficient-wallet error handling

Wallet payments are executed through database transaction logic.

---

## 🎁 Reward Points

StoreLedger includes a basic loyalty-points system.

### Current rule

```text
₹100 spent = 1 reward point
```

Reward points are:

- Calculated through a MySQL function
- Added through a stored procedure
- Automatically credited after eligible purchases

---

## 🧾 Billing System

The Billing module is one of the main parts of StoreLedger.

### Features

- Product search
- Add products to cart
- Change quantity
- Remove items
- Stock validation
- Maximum quantity validation
- Customer selection
- Walk-in customers
- Cash payment
- Card payment
- UPI payment
- Wallet payment
- Tax calculation
- Discount calculation
- Reward points
- Automatic stock reduction
- Database transaction support
- Row locking
- Invoice generation

---

## 💳 Supported Payment Methods

StoreLedger currently supports:

- Cash
- Card
- UPI
- Wallet

---

## 🧮 Automatic Discounts

Discount calculation is performed using a MySQL function.

Current discount rules:

| Bill Amount | Discount |
|---|---:|
| Below ₹1,000 | 0% |
| ₹1,000+ | 5% |
| ₹5,000+ | 10% |
| ₹10,000+ | 15% |

---

## 🧾 Invoice / Bill View

After successful billing, StoreLedger displays an invoice containing:

- Invoice ID
- Customer information
- Payment method
- Product details
- Quantity
- Price
- Subtotal
- Tax
- Discount
- Final total

Bills can also be downloaded as a `.txt` file.

---

## 📜 Bill History

The Bill History module provides:

- Previous bills
- Invoice search
- Customer search
- Payment-method search
- Bill details
- TXT bill download

---

## 📈 Reports

The Reports module contains sales and business information including:

- Total revenue
- Total orders
- Total customers
- Total products sold
- Daily sales
- Top-selling products
- Payment-method distribution
- Category-wise reports

---

## 🏠 Dashboard

The dashboard provides quick system statistics.

Current cards include:

- Total Products
- Total Customers
- Total Orders
- Low Stock
- Today's Revenue
- Bills Today
- Expiry Alerts

---

## 🧾 Audit Logs

Product changes are automatically recorded using MySQL triggers.

Audit information includes:

- Table name
- Operation
- Record ID
- Old values
- New values
- Change time

Current product auditing includes:

- Product updates
- Product deletions

---

## 🔐 Authentication

StoreLedger includes authentication using Flask sessions.

### Features

- Login
- Logout
- Session-based access control
- Password hashing using Werkzeug
- Protected application routes
- Logged-in user display

Passwords are stored as hashes rather than plain-text values.

---

## 🌙 Dark Mode

The UI supports:

- Light theme
- Dark theme
- Theme persistence using browser `localStorage`
- System-theme detection
- Responsive navigation

---

## 📱 Responsive Design

The interface contains responsive layouts for:

- Dashboard
- Inventory
- Billing
- Forms
- Tables
- Customer pages
- Sidebar
- Mobile navigation

---

# 🧠 Database Concepts Demonstrated

StoreLedger demonstrates multiple DBMS concepts.

## Stored Functions

- `calculate_discount`
- `calculate_reward_points`

## Stored Procedures

- `process_order_item`
- `process_wallet_payment`
- `add_reward_points`

## Triggers

- Product update audit trigger
- Product delete audit trigger

## Views

- `low_stock_view`
- `daily_sales_view`
- `expiry_products_view`

## Transactions

Billing uses:

- `START TRANSACTION`
- `COMMIT`
- `ROLLBACK`

## Concurrency Protection

The project uses:

```sql
SELECT ... FOR UPDATE
```

to lock products while billing and reduce the possibility of overselling.

## Error Handling

MySQL `SIGNAL` and Flask-side exception handling are used for cases such as:

- Product not found
- Invalid quantity
- Insufficient stock
- Invalid customer
- Insufficient wallet balance
- Expired products

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 |
| Styling | CSS3 |
| Client-side Logic | Vanilla JavaScript |
| Backend | Python |
| Web Framework | Flask |
| Database | MySQL |
| DB Connector | mysql-connector-python |
| Environment Variables | python-dotenv |
| Password Security | Werkzeug |
| Database GUI | MySQL Workbench |
| Code Editor | Visual Studio Code |
| Version Control | Git |
| Repository Hosting | GitHub |
| Browser | Chrome / Edge / Firefox / any modern browser |
| Windows Launcher | Batch file (`.bat`) |

---

# 📁 Project Structure

```text
StoreLedger/
│
├── app.py
├── db.py
├── requirements.txt
├── run_storeledger.bat
│
├── .env
├── .env.example
├── .gitignore
│
├── database/
│   ├── schema.sql
│   │
│   ├── functions/
│   │   ├── calculate_discount.sql
│   │   └── calculate_reward_points.sql
│   │
│   ├── procedures/
│   │   ├── process_order_item.sql
│   │   ├── process_wallet_payment.sql
│   │   └── add_reward_points.sql
│   │
│   ├── triggers/
│   │   ├── product_update_audit.sql
│   │   └── product_delete_audit.sql
│   │
│   └── views/
│       ├── low_stock_view.sql
│       ├── daily_sales_view.sql
│       └── expiry_products_view.sql
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── app.js
│       └── billing.js
│
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── products.html
    ├── add_product.html
    ├── edit_product.html
    ├── inventory.html
    ├── low_stock.html
    ├── expiry_products.html
    ├── restock_product.html
    ├── categories.html
    ├── add_category.html
    ├── edit_category.html
    ├── category_report.html
    ├── suppliers.html
    ├── add_supplier.html
    ├── edit_supplier.html
    ├── customers.html
    ├── add_customer.html
    ├── edit_customer.html
    ├── customer_details.html
    ├── add_wallet_balance.html
    ├── billing.html
    ├── view_bill.html
    ├── bill_history.html
    ├── reports.html
    └── audit_logs.html
```

> The exact structure may change slightly as the project evolves.

---

# ✅ Requirements

Before running StoreLedger, install:

## 1. Python

Recommended:

```text
Python 3.10+
```

Download Python from the official Python website.

During installation, enable:

```text
Add Python to PATH
```

Check installation:

```powershell
python --version
```

---

## 2. MySQL Server

Install MySQL Server.

The database must be running before StoreLedger can connect to it.

---

## 3. MySQL Workbench

MySQL Workbench is recommended for:

- Creating the database
- Running SQL scripts
- Viewing tables
- Testing functions
- Testing procedures
- Testing triggers
- Managing data

Workbench itself does not need to remain open while StoreLedger is running.

Only the MySQL Server must be available.

---

## 4. Visual Studio Code

VS Code is recommended for development, but **it is not required every time you run the project**.

Once the project is configured, StoreLedger can be started through:

```text
run_storeledger.bat
```

without opening VS Code.

---

## 5. Browser

Any modern browser can be used.

Examples:

- Google Chrome
- Microsoft Edge
- Mozilla Firefox

---

# 📥 Installation

## Step 1 — Clone the Repository

```powershell
git clone https://github.com/tushar-011/StoreLedger.git
```

Open the project folder:

```powershell
cd StoreLedger
```

---

## Step 2 — Create a Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

---

## Step 3 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

The project currently uses packages such as:

```text
Flask
mysql-connector-python
python-dotenv
```

Werkzeug is installed as a Flask dependency.

---

# 🗄️ Database Setup

Open MySQL Workbench.

Create/use the StoreLedger database and run the SQL files provided in the `database` directory.

Main schema:

```text
database/schema.sql
```

Then run SQL scripts for:

```text
database/functions/
database/procedures/
database/triggers/
database/views/
```

The expected database name is:

```text
storeledger
```

---

# ⚙️ Environment Configuration

Create:

```text
.env
```

in the project root.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=storeledger

SECRET_KEY=your_secure_secret_key
```

Do **not** commit `.env` to GitHub.

A safe template is provided through:

```text
.env.example
```

---

# ▶️ Running the Application

There are two ways to run StoreLedger.

---

## Method 1 — BAT Launcher

Recommended for demonstrations.

Simply double-click:

```text
run_storeledger.bat
```

The launcher:

1. Moves to the StoreLedger project directory
2. Uses the project's virtual environment
3. Starts Flask
4. Opens the browser automatically

You do **not** need to manually type:

```powershell
python app.py
```

when using the BAT launcher.

---

# ▶️ Using the BAT Launcher

Expected project location:

```text
StoreLedger/
├── app.py
├── run_storeledger.bat
└── venv/
```

Double-click:

```text
run_storeledger.bat
```

The application should open at:

```text
http://127.0.0.1:5000
```

To stop StoreLedger:

```text
Ctrl + C
```

inside the Command Prompt window running Flask.

> Important: MySQL Server must be running before starting StoreLedger.

---

## Method 2 — Manual Run

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

Then:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🔑 Login

An administrator account must exist in the `users` table.

Example credentials used during development:

```text
Username: admin
Password: admin123
```

> For real deployments, use a strong password and never publish real credentials.

Passwords are stored using Werkzeug password hashing.

---

# 🧩 Major Application Modules

```text
Dashboard
├── Sales overview
├── Low-stock statistics
├── Expiry alerts
└── Daily revenue

Products
├── Add
├── Edit
├── Delete
├── Search
├── Category
├── Supplier
├── Tax
├── Stock
└── Expiry

Categories
├── Add
├── Edit
├── Delete
└── Category reports

Inventory
├── Stock status
├── Low-stock products
├── Out-of-stock products
├── Restocking
└── Expiry management

Suppliers
├── Add
├── Edit
├── Delete
└── Product linkage

Customers
├── CRUD
├── Search
├── Wallet
├── Rewards
└── Purchase history

Billing
├── Cart
├── Tax
├── Discounts
├── Stock validation
├── Wallet payments
├── Reward points
└── Invoice generation

Reports
├── Revenue
├── Orders
├── Products sold
├── Daily sales
├── Top products
├── Payment distribution
└── Category report

Audit Logs
└── Database-triggered product auditing
```

---

# 🗃️ Important Database Objects

## Main Tables

StoreLedger currently uses tables including:

- `users`
- `categories`
- `products`
- `customers`
- `orders`
- `order_items`
- `wallet_transactions`
- `suppliers`
- `audit_log`

---

## Relationships

Examples:

```text
Category
   │
   └── Products

Supplier
   │
   └── Products

Customer
   │
   ├── Orders
   └── Wallet Transactions

Order
   │
   └── Order Items

Product
   │
   └── Order Items
```

---

# 🧪 Testing

Before submitting or demonstrating StoreLedger, test:

- Login
- Logout
- Product CRUD
- Category CRUD
- Customer CRUD
- Supplier CRUD
- Product search
- Inventory
- Low-stock detection
- Restocking
- Expiry handling
- Billing
- Cash payment
- Card payment
- UPI payment
- Wallet payment
- Insufficient-wallet validation
- Stock validation
- Reward points
- Bill history
- Bill download
- Reports
- Audit logs
- Dark mode
- BAT launcher

---

# 🔒 Security Notes

StoreLedger includes basic security measures appropriate for a mini-project:

- Password hashing
- Flask sessions
- Environment variables
- Parameterized SQL queries
- Backend validation
- Transaction rollback
- Database row locking
- `.env` excluded from Git

For production deployment, additional security hardening would be required.

---

# 🔮 Future Improvements

Possible future additions include:

- PDF invoices
- Barcode billing
- QR billing
- Advanced pagination
- Refund workflow
- Stock movement history
- Purchase orders
- Supplier purchase history
- Charts and analytics
- Role-based access control
- Cloud deployment
- Database backup UI
- Email invoices
- Multi-store support

These are intentionally left outside the current mini-project scope.

---

# 🌐 GitHub Setup

Useful Git commands:

```powershell
git status
git add .
git commit -m "Your commit message"
git push
```

For the final project commit:

```powershell
git add .
git commit -m "Finalize StoreLedger mini project"
git push
```

---

# 🏁 Project Status

### ✅ Mini-project feature development complete

StoreLedger currently includes the major features required to demonstrate:

- Full-stack development
- Relational database design
- CRUD operations
- Transaction management
- Stored programming
- Authentication
- Reporting
- Inventory management
- Billing logic
- Audit logging

The project is now primarily in its **testing, documentation, and submission stage**.

---

# 👨‍💻 Development Notes

StoreLedger was created as an academic mini-project with emphasis on database concepts and practical application development.

It is intended for learning, demonstration, and academic submission rather than production use.

---

<div align="center">

## 🧾 StoreLedger

**Billing • Inventory • Customers • Suppliers • Reports • Database Programming**

Built with **Python + Flask + MySQL**

</div>

## 👨‍💻 Author

### Tushar Thakur

**MCA Data Science**  
**Chandigarh University**

[![GitHub](https://img.shields.io/badge/GitHub-tushar--011-181717?logo=github)](https://github.com/tushar-011)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Tushar%20Thakur-0A66C2?logo=linkedin)](https://www.linkedin.com/in/tushar-thakur-8848a7396)
[![Email](https://img.shields.io/badge/Email-artificial.thakur%40gmail.com-EA4335?logo=gmail)](mailto:artificial.thakur@gmail.com)

