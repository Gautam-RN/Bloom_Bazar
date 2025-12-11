import flask as fk
import mysql.connector as sql

app = fk.Flask(__name__)

def get_db_connection():
    connection = sql.connect(
        host='localhost',
        user='root',
        password='root',
        charset='utf8'
    )
    cursor = connection.cursor()

    # Ensure DB exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS flower;")
    cursor.execute("USE flower;")

    # Create table if not present
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flowers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50),
            color VARCHAR(50),
            quantity INT,
            price FLOAT,
            des VARCHAR(300)
        );
    """)

    return connection, cursor


@app.route('/')
def show():
    conn, cur = get_db_connection()
    cur.execute("SELECT * FROM flowers;")
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    return fk.render_template('index.html', flowers=flowers)


@app.route('/sell', methods=['GET', 'POST'])
def add():
    if fk.request.method == 'POST':
        name = fk.request.form['name']
        color = fk.request.form['colour']
        quantity = fk.request.form['quantity']
        price = fk.request.form['price']
        des = fk.request.form['description']

        conn, cur = get_db_connection()
        cur.execute("""
            INSERT INTO flowers (name, color, quantity, price, des)
            VALUES (%s, %s, %s, %s, %s);
        """, (name, color, quantity, price, des))

        conn.commit()
        cur.close()
        conn.close()

        return fk.redirect('/')

    return fk.render_template('sell.html')


@app.route('/checkout')
def checkout():
    flower_id = fk.request.args.get('id')

    conn, cur = get_db_connection()
    cur.execute("SELECT * FROM flowers WHERE id = %s;", (flower_id,))
    flower_data = cur.fetchone()
    cur.close()
    conn.close()

    if not flower_data:
        return "Flower not found", 404

    flower = {
        'id': flower_data[0],
        'name': flower_data[1],
        'color': flower_data[2],
        'quantity': flower_data[3],
        'price': flower_data[4],
        'des': flower_data[5]
    }

    return fk.render_template('checkout.html', flower=flower)


@app.route("/order", methods=["POST"])
def order():
    flower_id = fk.request.form["id"]
    qty = int(fk.request.form["qty"])

    # Create connection
    conn, cur = get_db_connection()

    # Get flower details
    cur.execute("SELECT * FROM flowers WHERE id = %s", (flower_id,))
    flower_data = cur.fetchone()

    if not flower_data:
        cur.close()
        conn.close()
        return "Flower not found", 404

    available_qty = flower_data[3]
    price_per_kg = flower_data[4]
    flower_name = flower_data[1]

    if qty > available_qty:
        cur.close()
        conn.close()
        return "Insufficient quantity", 400

    # Calculate total amount
    total = qty * price_per_kg

    # Update flower quantity
    new_qty = available_qty - qty
    cur.execute(
        "UPDATE flowers SET quantity = %s WHERE id = %s",
        (new_qty, flower_id)
    )
    conn.commit()

    # Create order_data for template
    order_data = {
        "id": flower_id,  # using flower id as order id (since you don't have an orders table)
        "flower_name": flower_name,
        "qty": qty,
        "total": total
    }

    cur.close()
    conn.close()

    return fk.render_template("order_success.html", order=order_data)

if __name__ == '__main__':
    app.run(debug=True)
