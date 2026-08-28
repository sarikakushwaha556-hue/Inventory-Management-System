from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Total number of products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total number of categories
    cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
    total_categories = cursor.fetchone()[0]

    # Products with quantity 5 or less
    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= 5")
    low_stock = cursor.fetchone()[0]

    # Get low stock products
    cursor.execute("SELECT * FROM products WHERE quantity <= 5")
    low_stock_products = cursor.fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        low_stock_products=low_stock_products
    )


@app.route("/add-product")
def add_product():
    return render_template("add_product.html")


@app.route("/view-products")
def view_products():

    search = request.args.get("search", "")

    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if search:
        cursor.execute(
            """
            SELECT * FROM products
            WHERE product_name LIKE ?
            OR category LIKE ?
            OR brand LIKE ?
            """,
            (
                "%" + search + "%",
                "%" + search + "%",
                "%" + search + "%"
            )
        )
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    connection.close()

    return render_template(
        "view_products.html",
        products=products
    )


@app.route("/edit-product/<int:product_id>")
def edit_product(product_id):

    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    connection.close()

    return render_template("edit_product.html", product=product)


@app.route("/update-product/<int:product_id>", methods=["POST"])
def update_product(product_id):

    product_name = request.form["product_name"]
    category = request.form["category"]
    brand = request.form["brand"]
    price = request.form["price"]
    quantity = request.form["quantity"]

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET product_name = ?,
            category = ?,
            brand = ?,
            price = ?,
            quantity = ?
        WHERE id = ?
    """, (product_name, category, brand, price, quantity, product_id))

    connection.commit()
    connection.close()

    return redirect("/view-products")


@app.route("/delete-product/<int:product_id>")
def delete_product(product_id):

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/view-products")


@app.route("/save-product", methods=["POST"])
def save_product():

    product_name = request.form["product_name"]
    category = request.form["category"]
    brand = request.form["brand"]
    price = request.form["price"]
    quantity = request.form["quantity"]

    if not product_name.strip() or not category.strip() or not brand.strip():
        return "Product name, category and brand cannot be empty"

    # Backend validation
    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return "Invalid price or quantity"

    if price < 0 or quantity < 0:
        return "Price and quantity cannot be negative"

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products(product_name, category, brand, price, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (product_name, category, brand, price, quantity))

    connection.commit()
    connection.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)


    