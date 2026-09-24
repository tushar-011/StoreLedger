import json
from flask import(
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    Response
)
from db import get_db_connection


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/database-test")
def database_test():
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")

        database_name = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return f"Database connected successfully: {database_name}"

    except Exception as error:
        return f"Database connection failed: {error}"


@app.route("/categories")
def categories():
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM categories")

    category_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return category_data

@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE stock <= minimum_stock
        """
    )

    low_stock = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock=low_stock
    )

@app.route("/products/add", methods=["GET", "POST"])
def add_product():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form.get("category_id") or None
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
                price,
                stock,
                minimum_stock,
                tax_rate,
                expiry_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                product_name,
                category_id,
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

        return redirect(url_for("products"))

    cursor.execute(
        """
        SELECT *
        FROM categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_product.html",
        categories=categories
    )

@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    connection = get_db_connection()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form.get("category_id") or None
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

        return redirect(url_for("products"))

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

    cursor.execute(
        """
        SELECT *
        FROM categories
        ORDER BY category_name
        """
    )

    categories = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories
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
            products.*,
            categories.category_name
        FROM products
        LEFT JOIN categories
            ON products.category_id = categories.category_id
        WHERE products.product_name LIKE %s
        ORDER BY products.product_id DESC
        """,
        (f"%{search}%",)
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
            products.*,
            categories.category_name
        FROM products
        LEFT JOIN categories
            ON products.category_id = categories.category_id
        ORDER BY products.product_name
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
        SELECT
            products.*,
            categories.category_name
        FROM products
        LEFT JOIN categories
            ON products.category_id = categories.category_id
        WHERE products.stock <= products.minimum_stock
        ORDER BY products.stock ASC
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
        SELECT *
        FROM products
        WHERE product_id = %s
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
            tax_rate
        FROM products
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
                raise ValueError(
                    "Invalid product quantity."
                )

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
                raise ValueError(
                    "Product not found."
                )

            if quantity > product["stock"]:
                raise ValueError(
                    f"Insufficient stock for "
                    f"{product['product_name']}."
                )

            price = float(product["price"])

            tax_rate = float(
                product["tax_rate"] or 0
            )

            item_subtotal = (
                price * quantity
            )

            item_tax = (
                item_subtotal
                * tax_rate
                / 100
            )

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

        discount = 0

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

            order_cursor.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE product_id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )

        connection.commit()

        return redirect(
            url_for(
                "view_bill",
                order_id=order_id
            )
        )

    except Exception as error:

        if connection.is_connected():
            connection.rollback()

        return load_billing_page(
            str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if order_cursor is not None:
            order_cursor.close()

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


if __name__ == "__main__":
    app.run(debug=True)