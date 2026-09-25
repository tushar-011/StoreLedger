import json
from flask import(
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    Response,
    jsonify
)
import mysql.connector
from db import get_db_connection


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/database-test")
def database_test():
    try:
        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE();")

        database_name = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return f"Database connected successfully: {database_name}"

    except Exception as error:
        return f"Database connection failed: {error}"

@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM products
        """
    )
    total_products = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM customers
        """
    )
    total_customers = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM orders
        """
    )
    total_orders = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM low_stock_view
        """
    )

    low_stock_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT
            total_revenue,
            total_orders
        FROM daily_sales_view
        WHERE sale_date = CURDATE()
        """
    )

    today_sales = cursor.fetchone()

    if today_sales:
        today_revenue = today_sales["total_revenue"]
        today_orders = today_sales["total_orders"]
    else:
        today_revenue = 0
        today_orders = 0


    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM expiry_products_view
        WHERE expiry_status IN (
            'Expired',
            'Critical',
            'Expiring Soon'
        )
        """
    )

    expiry_alerts = cursor.fetchone()["total"]


    cursor.close()
    connection.close()


    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_count=low_stock_count,
        today_revenue=today_revenue,
        today_orders=today_orders,
        expiry_alerts=expiry_alerts
    )
    
@app.route("/products/add", methods=["GET", "POST"])
def add_product():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form.get("category_id") or None
        supplier_id = request.form.get("supplier_id") or None

        price = request.form["price"]
        stock = request.form["stock"]
        minimum_stock = request.form["minimum_stock"]
        tax_rate = request.form.get("tax_rate") or 0
        expiry_date = request.form.get("expiry_date") or None

        insert_cursor = connection.cursor()

        insert_cursor.execute(
            """
            INSERT INTO products
            (
                product_name,
                category_id,
                supplier_id,
                price,
                stock,
                minimum_stock,
                tax_rate,
                expiry_date
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                product_name,
                category_id,
                supplier_id,
                price,
                stock,
                minimum_stock,
                tax_rate,
                expiry_date
            )
        )

        connection.commit()

        insert_cursor.close()
        cursor.close()
        connection.close()

        return redirect(
            url_for("products")
        )

    cursor.execute(
        """
        SELECT *
        FROM categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM suppliers
        ORDER BY supplier_name
        """
    )

    suppliers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_product.html",
        categories=categories,
        suppliers=suppliers
    )

@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    connection = get_db_connection()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form.get("category_id") or None
        supplier_id = request.form.get("supplier_id") or None

        price = request.form["price"]
        stock = request.form["stock"]
        minimum_stock = request.form["minimum_stock"]
        tax_rate = request.form.get("tax_rate") or 0
        expiry_date = request.form.get("expiry_date") or None

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE products
            SET
                product_name = %s,
                category_id = %s,
                supplier_id = %s,
                price = %s,
                stock = %s,
                minimum_stock = %s,
                tax_rate = %s,
                expiry_date = %s
            WHERE product_id = %s
            """,
            (
                product_name,
                category_id,
                supplier_id,
                price,
                stock,
                minimum_stock,
                tax_rate,
                expiry_date,
                product_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            url_for("products")
        )

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE product_id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        cursor.close()
        connection.close()

        return "Product not found.", 404

    cursor.execute(
        """
        SELECT *
        FROM categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM suppliers
        ORDER BY supplier_name
        """
    )

    suppliers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories,
        suppliers=suppliers
    )
    
@app.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE product_id = %s
        """,
        (product_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("products"))

@app.route("/products")
def products():
    search = request.args.get("search", "")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.product_id,
            p.product_name,
            c.category_name,
            s.supplier_name,
            p.price,
            p.stock,
            p.minimum_stock,
            p.tax_rate,
            p.expiry_date
        FROM products p
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id
        WHERE p.product_name LIKE %s
        OR c.category_name LIKE %s
        OR s.supplier_name LIKE %s
        ORDER BY p.product_id DESC
        """,
        (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )
    )

    product_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "products.html",
        products=product_data,
        search=search
    )

@app.route("/inventory")
def inventory():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.product_id,
            p.product_name,
            c.category_name,
            s.supplier_name,
            p.stock,
            p.minimum_stock,
            p.expiry_date
        FROM products p
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id
        ORDER BY p.product_name
        """
    )

    product_data = cursor.fetchall()

    cursor.execute(
        """
        SELECT COUNT(*) AS total_products
        FROM products
        """
    )

    total_products = cursor.fetchone()["total_products"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(stock), 0) AS total_stock
        FROM products
        """
    )

    total_stock = cursor.fetchone()["total_stock"]

    cursor.execute(
        """
        SELECT COUNT(*) AS low_stock_count
        FROM products
        WHERE stock <= minimum_stock
        AND stock > 0
        """
    )

    low_stock_count = cursor.fetchone()["low_stock_count"]

    cursor.execute(
        """
        SELECT COUNT(*) AS out_of_stock_count
        FROM products
        WHERE stock = 0
        """
    )

    out_of_stock_count = cursor.fetchone()["out_of_stock_count"]

    cursor.close()
    connection.close()

    return render_template(
        "inventory.html",
        products=product_data,
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )

@app.route("/inventory/low-stock")
def low_stock():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM low_stock_view
        ORDER BY stock ASC
        """
    )

    product_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "low_stock.html",
        products=product_data
    )

@app.route("/inventory/restock/<int:product_id>", methods=["GET", "POST"])
def restock_product(product_id):

    connection = get_db_connection()

    if request.method == "POST":

        quantity = int(request.form["quantity"])

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE products
            SET stock = stock + %s
            WHERE product_id = %s
            """,
            (quantity, product_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("inventory"))

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.*,
            s.supplier_name,
            s.company_name,
            s.phone,
            s.email
        FROM products p
        LEFT JOIN suppliers s
            ON p.supplier_id = s.supplier_id
        WHERE p.product_id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "restock_product.html",
        product=product
    )

@app.route("/customers")
def customers():

    search = request.args.get("search", "")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_name LIKE %s
           OR phone LIKE %s
           OR email LIKE %s
        ORDER BY customer_id DESC
        """,
        (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )
    )

    customer_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "customers.html",
        customers=customer_data,
        search=search
    )

@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form.get("phone") or None
        email = request.form.get("email") or None
        wallet_balance = request.form.get("wallet_balance") or 0
        reward_points = request.form.get("reward_points") or 0

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO customers
            (
                customer_name,
                phone,
                email,
                wallet_balance,
                reward_points
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                customer_name,
                phone,
                email,
                wallet_balance,
                reward_points
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("customers"))

    return render_template("add_customer.html")

@app.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):

    connection = get_db_connection()

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form.get("phone") or None
        email = request.form.get("email") or None
        wallet_balance = request.form.get("wallet_balance") or 0
        reward_points = request.form.get("reward_points") or 0

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE customers
            SET
                customer_name = %s,
                phone = %s,
                email = %s,
                wallet_balance = %s,
                reward_points = %s
            WHERE customer_id = %s
            """,
            (
                customer_name,
                phone,
                email,
                wallet_balance,
                reward_points,
                customer_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("customers"))

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = %s
        """,
        (customer_id,)
    )

    customer = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_customer.html",
        customer=customer
    )

@app.route("/customers/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM customers
        WHERE customer_id = %s
        """,
        (customer_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("customers"))

def load_billing_page(error=None):

    connection = get_db_connection()

    cursor = connection.cursor(
            dictionary=True
        )

    cursor.execute(
        """
        SELECT
            product_id,
            product_name,
            price,
            stock,
            tax_rate,
            expiry_date
        FROM products
        WHERE expiry_date IS NULL
        OR expiry_date >= CURDATE()
        ORDER BY product_name
        """
    )

    products = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            customer_id,
            customer_name,
            phone
        FROM customers
        ORDER BY customer_name
        """
    )

    customers = cursor.fetchall()


    cursor.close()

    connection.close()


    return render_template(
        "billing.html",
        products=products,
        customers=customers,
        error=error
    )
@app.route("/billing", methods=["GET", "POST"])
def new_bill():
        
    if request.method == "GET":
        return load_billing_page()

    connection = get_db_connection()

    cursor = None
    order_cursor = None
    discount_cursor = None
    reward_cursor = None

    try:

        customer_id = request.form.get("customer_id") or None
        payment_method = request.form.get("payment_method")
        cart_json = request.form.get("cart_data")

        if not payment_method:
            raise ValueError("Please select a payment method.")

        if not cart_json:
            raise ValueError("Cart is empty.")

        cart_items = json.loads(cart_json)

        if len(cart_items) == 0:
            raise ValueError("Cart is empty.")

        connection.start_transaction()

        cursor = connection.cursor(dictionary=True)

        subtotal = 0
        tax_total = 0

        verified_items = []

        for item in cart_items:

            product_id = int(item["product_id"])
            quantity = int(item["quantity"])

            if quantity <= 0:
                raise ValueError("Invalid product quantity.")

            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    price,
                    stock,
                    tax_rate
                FROM products
                WHERE product_id = %s
                FOR UPDATE
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if not product:
                raise ValueError("Product not found.")

            if quantity > product["stock"]:
                raise ValueError(
                    f"Insufficient stock for {product['product_name']}."
                )

            price = float(product["price"])
            tax_rate = float(product["tax_rate"] or 0)

            item_subtotal = price * quantity
            item_tax = item_subtotal * tax_rate / 100

            subtotal += item_subtotal
            tax_total += item_tax

            verified_items.append(
                {
                    "product_id": product_id,
                    "product_name": product["product_name"],
                    "quantity": quantity,
                    "price": price
                }
            )

        discount_cursor = connection.cursor()

        discount_cursor.execute(
            """
            SELECT calculate_discount(%s)
            """,
            (subtotal,)
        )

        discount_result = discount_cursor.fetchone()

        discount = float(
            discount_result[0] or 0
        )

        total_amount = (
            subtotal
            + tax_total
            - discount
        )

        order_cursor = connection.cursor()

        order_cursor.execute(
            """
            INSERT INTO orders
            (
                customer_id,
                subtotal,
                discount,
                tax,
                total_amount,
                payment_method,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'completed'
            )
            """,
            (
                customer_id,
                subtotal,
                discount,
                tax_total,
                total_amount,
                payment_method
            )
        )

        order_id = order_cursor.lastrowid

        for item in verified_items:

            order_cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"]
                )
            )

            order_cursor.callproc(
                "process_order_item",
                (
                    item["product_id"],
                    item["quantity"]
                )
            )

            if payment_method == "Wallet":

                if customer_id is None:
                    raise ValueError(
                        "Please select a customer for wallet payment."
                    )

                order_cursor.callproc(
                    "process_wallet_payment",
                    (
                        int(customer_id),
                        total_amount,
                        order_id
                    )
                )


            print("CUSTOMER ID:", customer_id)
            print("TOTAL AMOUNT:", total_amount)


            if customer_id is not None:

                reward_cursor = connection.cursor()

                reward_cursor.execute(
                    """
                    CALL add_reward_points(%s, %s)
                    """,
                    (
                        int(customer_id),
                        total_amount
                    )
                )

                reward_cursor.close()


            connection.commit()

        return redirect(
            url_for(
                "view_bill",
                order_id=order_id
            )
        )

    except mysql.connector.Error as error:

        if connection.is_connected():
            connection.rollback()

        error_message = str(error)

        if "Insufficient stock" in error_message:
            error_message = (
                "Insufficient stock. "
                "Please reduce the requested quantity."
            )

        elif "Invalid quantity" in error_message:
            error_message = (
                "Invalid quantity. "
                "Quantity must be greater than zero."
            )

        elif "Product not found" in error_message:
            error_message = (
                "One of the selected products no longer exists."
            )

        elif "Insufficient wallet balance" in error_message:
            error_message = (
                "Insufficient wallet balance. "
                "Please add money to the wallet or choose another payment method."
            )

        elif "Invalid customer account" in error_message:
            error_message = (
                "The selected customer account is invalid."
            )
            
        else:
            error_message = (
                "Database error: "
                + error_message
            )

        return load_billing_page(
            error_message
        )

    except ValueError as error:

        if connection.is_connected():
            connection.rollback()

        return load_billing_page(
            str(error)
        )

    except Exception:

        if connection.is_connected():
            connection.rollback()

        return load_billing_page(
            "Something went wrong while generating the bill."
        )

    finally:

        if cursor is not None:
            cursor.close()

        if discount_cursor is not None:
            discount_cursor.close()

        if order_cursor is not None:
            order_cursor.close()

        if reward_cursor is not None:
            reward_cursor.close()

        if connection.is_connected():
            connection.close()
            

@app.route("/bill/<int:order_id>")
def view_bill(order_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                orders.*,
                customers.customer_name
            FROM orders
            LEFT JOIN customers
                ON orders.customer_id =
                   customers.customer_id
            WHERE orders.order_id = %s
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if not order:
            return "Bill not found.", 404

        cursor.execute(
            """
            SELECT
                order_items.*,
                products.product_name
            FROM order_items
            JOIN products
                ON order_items.product_id =
                   products.product_id
            WHERE order_items.order_id = %s
            ORDER BY order_items.order_item_id
            """,
            (order_id,)
        )

        items = cursor.fetchall()

        return render_template(
            "view_bill.html",
            order=order,
            items=items
        )

    finally:

        cursor.close()

        if connection.is_connected():
            connection.close()

@app.route("/bills")
def bill_history():

    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    search_pattern = f"%{search}%"

    cursor.execute(
        """
        SELECT
            orders.order_id,
            orders.order_date,
            orders.payment_method,
            orders.status,
            orders.total_amount,
            customers.customer_name
        FROM orders
        LEFT JOIN customers
            ON orders.customer_id =
               customers.customer_id
        WHERE
            CAST(orders.order_id AS CHAR) LIKE %s
            OR COALESCE(customers.customer_name, '') LIKE %s
            OR COALESCE(orders.payment_method, '') LIKE %s
        ORDER BY orders.order_id DESC
        """,
        (
            search_pattern,
            search_pattern,
            search_pattern
        )
    )

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "bill_history.html",
        orders=orders,
        search=search
    )

@app.route("/bill/<int:order_id>/download")
def download_bill(order_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                orders.*,
                customers.customer_name,
                customers.phone
            FROM orders
            LEFT JOIN customers
                ON orders.customer_id =
                   customers.customer_id
            WHERE orders.order_id = %s
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if not order:
            return "Bill not found.", 404

        cursor.execute(
            """
            SELECT
                order_items.quantity,
                order_items.price,
                products.product_name
            FROM order_items
            JOIN products
                ON order_items.product_id =
                   products.product_id
            WHERE order_items.order_id = %s
            ORDER BY order_items.order_item_id
            """,
            (order_id,)
        )

        items = cursor.fetchall()

        customer_name = (
            order["customer_name"]
            or "Walk-in Customer"
        )

        lines = []

        lines.append(
            "========================================"
        )

        lines.append(
            "              STORELEDGER"
        )

        lines.append(
            "========================================"
        )

        lines.append(
            f"Invoice ID : #{order['order_id']}"
        )

        lines.append(
            f"Date       : {order['order_date']}"
        )

        lines.append(
            f"Customer   : {customer_name}"
        )

        if order["phone"]:
            lines.append(
                f"Phone      : {order['phone']}"
            )

        lines.append(
            f"Payment    : {order['payment_method']}"
        )

        lines.append(
            f"Status     : {order['status']}"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            "ITEMS"
        )

        lines.append(
            "----------------------------------------"
        )

        for item in items:

            item_total = (
                float(item["price"])
                * item["quantity"]
            )

            lines.append(
                f"{item['product_name']}"
            )

            lines.append(
                f"  {item['quantity']} x "
                f"Rs.{float(item['price']):.2f}"
                f" = Rs.{item_total:.2f}"
            )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"Subtotal : Rs."
            f"{float(order['subtotal']):.2f}"
        )

        lines.append(
            f"Tax      : Rs."
            f"{float(order['tax']):.2f}"
        )

        lines.append(
            f"Discount : Rs."
            f"{float(order['discount']):.2f}"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"TOTAL    : Rs."
            f"{float(order['total_amount']):.2f}"
        )

        lines.append(
            "========================================"
        )

        lines.append(
            "Thank you for shopping with StoreLedger!"
        )

        lines.append(
            "========================================"
        )

        bill_text = "\n".join(lines)

        filename = (
            f"StoreLedger_Invoice_"
            f"{order_id}.txt"
        )

        return Response(
            bill_text,
            mimetype="text/plain",
            headers={
                "Content-Disposition":
                    f"attachment; filename={filename}"
            }
        )

    finally:

        cursor.close()

        if connection.is_connected():
            connection.close()

@app.route("/audit-logs")
def audit_logs():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM audit_log
        ORDER BY log_id DESC
        """
    )

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "audit_logs.html",
        logs=logs
    )

@app.route(
    "/customers/<int:customer_id>/wallet/add",
    methods=["GET", "POST"]
)
def add_wallet_balance(customer_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = %s
        """,
        (customer_id,)
    )

    customer = cursor.fetchone()

    if not customer:

        cursor.close()
        connection.close()

        return "Customer not found.", 404

    if request.method == "POST":

        try:

            amount = float(
                request.form["amount"]
            )

            if amount <= 0:
                raise ValueError(
                    "Amount must be greater than zero."
                )

            new_balance = (
                float(customer["wallet_balance"])
                + amount
            )

            update_cursor = connection.cursor()

            update_cursor.execute(
                """
                UPDATE customers
                SET wallet_balance = wallet_balance + %s
                WHERE customer_id = %s
                """,
                (
                    amount,
                    customer_id
                )
            )

            update_cursor.execute(
                """
                INSERT INTO wallet_transactions
                (
                    customer_id,
                    transaction_type,
                    amount,
                    balance_after
                )
                VALUES
                (%s, 'CREDIT', %s, %s)
                """,
                (
                    customer_id,
                    amount,
                    new_balance
                )
            )

            connection.commit()

            update_cursor.close()
            cursor.close()
            connection.close()

            return redirect(
                url_for("customers")
            )

        except ValueError:

            cursor.close()
            connection.close()

            return "Invalid wallet amount.", 400

    cursor.close()
    connection.close()

    return render_template(
        "add_wallet_balance.html",
        customer=customer
    )
    
@app.route("/customers/<int:customer_id>")
def customer_details(customer_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = %s
        """,
        (customer_id,)
    )

    customer = cursor.fetchone()

    if not customer:
        cursor.close()
        connection.close()

        return "Customer not found.", 404

    cursor.execute(
        """
        SELECT *
        FROM wallet_transactions
        WHERE customer_id = %s
        ORDER BY wallet_transaction_id DESC
        """,
        (customer_id,)
    )

    wallet_transactions = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            orders.order_id,
            orders.order_date,
            orders.total_amount,
            orders.payment_method,
            orders.status
        FROM orders
        WHERE customer_id = %s
        ORDER BY orders.order_id DESC
        """,
        (customer_id,)
    )

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "customer_details.html",
        customer=customer,
        wallet_transactions=wallet_transactions,
        orders=orders
    )
    
@app.route("/reports")
def reports():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(total_amount), 0) AS total_revenue,
            COUNT(*) AS total_orders
        FROM orders
        WHERE status = 'completed'
        """
    )

    totals = cursor.fetchone()

    total_revenue = totals["total_revenue"]
    total_orders = totals["total_orders"]


    cursor.execute(
        """
        SELECT COUNT(*) AS total_customers
        FROM customers
        """
    )

    total_customers = (
        cursor.fetchone()["total_customers"]
    )


    cursor.execute(
        """
        SELECT
            COALESCE(SUM(quantity), 0)
            AS total_products_sold
        FROM order_items
        """
    )

    total_products_sold = (
        cursor.fetchone()["total_products_sold"]
    )


    cursor.execute(
        """
        SELECT *
        FROM daily_sales_view
        ORDER BY sale_date DESC
        """
    )

    daily_sales = cursor.fetchall()


    cursor.execute(
        """
        SELECT
            products.product_name,
            SUM(order_items.quantity)
                AS total_quantity,
            SUM(
                order_items.quantity
                * order_items.price
            ) AS revenue
        FROM order_items

        JOIN products
            ON order_items.product_id =
               products.product_id

        GROUP BY
            products.product_id,
            products.product_name

        ORDER BY
            total_quantity DESC

        LIMIT 10
        """
    )

    top_products = cursor.fetchall()


    cursor.execute(
        """
        SELECT
            payment_method,
            COUNT(*) AS total_orders,
            SUM(total_amount) AS total_amount
        FROM orders

        WHERE status = 'completed'

        GROUP BY payment_method

        ORDER BY total_orders DESC
        """
    )

    payment_summary = cursor.fetchall()


    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        total_products_sold=total_products_sold,
        daily_sales=daily_sales,
        top_products=top_products,
        payment_summary=payment_summary
    )
    
@app.route("/inventory/expiry")
def expiry_products():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM expiry_products_view
        ORDER BY expiry_date ASC
        """
    )

    products = cursor.fetchall()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM expiry_products_view
        WHERE expiry_status = 'Expired'
        """
    )

    expired_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM expiry_products_view
        WHERE expiry_status = 'Critical'
        """
    )

    critical_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM expiry_products_view
        WHERE expiry_status = 'Expiring Soon'
        """
    )

    expiring_count = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "expiry_products.html",
        products=products,
        expired_count=expired_count,
        critical_count=critical_count,
        expiring_count=expiring_count
    )
    
@app.route("/suppliers")
def suppliers():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM suppliers
        ORDER BY supplier_id DESC
        """
    )

    supplier_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "suppliers.html",
        suppliers=supplier_data
    )
    
@app.route("/suppliers/add", methods=["GET", "POST"])
def add_supplier():

    if request.method == "POST":

        supplier_name = request.form["supplier_name"]
        company_name = request.form.get("company_name") or None
        phone = request.form.get("phone") or None
        email = request.form.get("email") or None
        address = request.form.get("address") or None

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO suppliers
            (
                supplier_name,
                company_name,
                phone,
                email,
                address
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                supplier_name,
                company_name,
                phone,
                email,
                address
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            url_for("suppliers")
        )

    return render_template(
        "add_supplier.html"
    )
    
@app.route(
    "/suppliers/edit/<int:supplier_id>",
    methods=["GET", "POST"]
)
def edit_supplier(supplier_id):

    connection = get_db_connection()

    if request.method == "POST":

        supplier_name = request.form["supplier_name"]
        company_name = request.form.get("company_name") or None
        phone = request.form.get("phone") or None
        email = request.form.get("email") or None
        address = request.form.get("address") or None

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE suppliers
            SET
                supplier_name = %s,
                company_name = %s,
                phone = %s,
                email = %s,
                address = %s
            WHERE supplier_id = %s
            """,
            (
                supplier_name,
                company_name,
                phone,
                email,
                address,
                supplier_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            url_for("suppliers")
        )

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM suppliers
        WHERE supplier_id = %s
        """,
        (supplier_id,)
    )

    supplier = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_supplier.html",
        supplier=supplier
    )
    
@app.route(
    "/suppliers/delete/<int:supplier_id>",
    methods=["POST"]
)
def delete_supplier(supplier_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM suppliers
        WHERE supplier_id = %s
        """,
        (supplier_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for("suppliers")
    )
    
@app.route("/api/categories")
def categories_api():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(categories)

@app.route("/categories")
def category_list():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            c.category_id,
            c.category_name,
            COUNT(p.product_id) AS product_count
        FROM categories c

        LEFT JOIN products p
            ON c.category_id = p.category_id

        GROUP BY
            c.category_id,
            c.category_name

        ORDER BY c.category_name
        """
    )

    category_data = cursor.fetchall()

    error = request.args.get("error")

    cursor.close()
    connection.close()

    return render_template(
        "categories.html",
        categories=category_data,
        error=error
    )
    
@app.route("/categories/add", methods=["GET", "POST"])
def add_category():

    if request.method == "POST":

        category_name = request.form["category_name"].strip()

        if not category_name:
            return render_template(
                "add_category.html",
                error="Category name is required."
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO categories
                (
                    category_name
                )
                VALUES (%s)
                """,
                (category_name,)
            )

            connection.commit()

        except mysql.connector.IntegrityError:

            cursor.close()
            connection.close()

            return render_template(
                "add_category.html",
                error="Category already exists."
            )

        cursor.close()
        connection.close()

        return redirect(
            url_for("category_list")
        )

    return render_template(
        "add_category.html"
    )
    
@app.route(
    "/categories/edit/<int:category_id>",
    methods=["GET", "POST"]
)
def edit_category(category_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        category_name = request.form["category_name"].strip()

        if not category_name:

            cursor.close()
            connection.close()

            return render_template(
                "edit_category.html",
                category={
                    "category_id": category_id,
                    "category_name": category_name
                },
                error="Category name is required."
            )

        try:

            update_cursor = connection.cursor()

            update_cursor.execute(
                """
                UPDATE categories
                SET category_name = %s
                WHERE category_id = %s
                """,
                (
                    category_name,
                    category_id
                )
            )

            connection.commit()

            update_cursor.close()

        except mysql.connector.IntegrityError:

            cursor.close()
            connection.close()

            return render_template(
                "edit_category.html",
                category={
                    "category_id": category_id,
                    "category_name": category_name
                },
                error="Another category already has this name."
            )

        cursor.close()
        connection.close()

        return redirect(
            url_for("category_list")
        )

    cursor.execute(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        WHERE category_id = %s
        """,
        (category_id,)
    )

    category = cursor.fetchone()

    cursor.close()
    connection.close()

    if not category:
        return "Category not found.", 404

    return render_template(
        "edit_category.html",
        category=category
    )
    
@app.route(
    "/categories/delete/<int:category_id>",
    methods=["POST"]
)
def delete_category(category_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM products
        WHERE category_id = %s
        """,
        (category_id,)
    )

    product_count = cursor.fetchone()["total"]

    if product_count > 0:

        cursor.close()
        connection.close()

        return redirect(
            url_for(
                "category_list",
                error=(
                    "Category cannot be deleted "
                    "because products are using it."
                )
            )
        )

    delete_cursor = connection.cursor()

    delete_cursor.execute(
        """
        DELETE FROM categories
        WHERE category_id = %s
        """,
        (category_id,)
    )

    connection.commit()

    delete_cursor.close()
    cursor.close()
    connection.close()

    return redirect(
        url_for("category_list")
    )
    
@app.route("/reports/categories")
def category_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            c.category_id,
            c.category_name,

            COALESCE(
                product_stats.product_count,
                0
            ) AS product_count,

            COALESCE(
                product_stats.total_stock,
                0
            ) AS total_stock,

            COALESCE(
                product_stats.inventory_value,
                0
            ) AS inventory_value,

            COALESCE(
                sales_stats.units_sold,
                0
            ) AS units_sold,

            COALESCE(
                sales_stats.sales_revenue,
                0
            ) AS sales_revenue

        FROM categories c

        LEFT JOIN
        (
            SELECT
                category_id,
                COUNT(*) AS product_count,
                SUM(stock) AS total_stock,
                SUM(stock * price) AS inventory_value
            FROM products
            GROUP BY category_id
        ) AS product_stats

            ON c.category_id =
               product_stats.category_id

        LEFT JOIN
        (
            SELECT
                p.category_id,
                SUM(oi.quantity) AS units_sold,
                SUM(
                    oi.quantity * oi.price
                ) AS sales_revenue

            FROM order_items oi

            JOIN products p
                ON oi.product_id = p.product_id

            JOIN orders o
                ON oi.order_id = o.order_id

            WHERE o.status = 'completed'

            GROUP BY p.category_id

        ) AS sales_stats

            ON c.category_id =
               sales_stats.category_id

        ORDER BY
            sales_revenue DESC,
            c.category_name ASC
        """
    )

    report_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "category_report.html",
        categories=report_data
    )
    

if __name__ == "__main__":
    app.run(debug=True)