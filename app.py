from flask import Flask, render_template

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


if __name__ == "__main__":
    app.run(debug=True)