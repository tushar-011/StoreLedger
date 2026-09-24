from flask import Flask, render_template, request, redirect, url_for
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

    
if __name__ == "__main__":
    app.run(debug=True)