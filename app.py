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

@app.route("/products")
def products():
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
        ORDER BY products.product_id DESC
        """
    )

    product_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "products.html",
        products=product_data
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
    
if __name__ == "__main__":
    app.run(debug=True)