from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import xml.etree.ElementTree as ET
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    products = []
    if os.path.exists("inventory.xml"):
        tree = ET.parse("inventory.xml")
        root = tree.getroot()
        for product_elem in root.findall('product'):
            product = {
                "id": product_elem.find('id').text,
                "barCode": product_elem.find('barCode').text,
                "type": product_elem.find('type').text,
                "name": product_elem.find('name').text,
                "purchasePrice": product_elem.find('purchasePrice').text,
                "salePrice": product_elem.find('salePrice').text,
                "stock": product_elem.find('stock').text,
                "totalPurchasePrice": product_elem.find('totalPurchasePrice').text,
                "totalSalePrice": product_elem.find('totalSalePrice').text,
                "saleable": product_elem.find('saleable').text,
            }
            products.append(product)
    return render_template('inventory.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_id = request.form['productId']
    bar_code = request.form['productBarCode']
    product_type = request.form['productType']
    product_name = request.form['productName']
    purchase_price = request.form['purchasePrice']
    sale_price = request.form['salePrice']
    stock = request.form['stock']
    total_purchase_price = str(float(purchase_price) * int(stock))
    total_sale_price = str(float(sale_price) * int(stock))
    saleable = request.form['saleable']

    if not os.path.exists("inventory.xml"):
        root = ET.Element("inventory")
        tree = ET.ElementTree(root)
    else:
        tree = ET.parse("inventory.xml")
        root = tree.getroot()

    # Check for existing product ID or barcode
    for product in root.findall('product'):
        if product.find('id').text == product_id or product.find('barCode').text == bar_code:
            flash("Product ID or BarCode already exists!", "error")
            return redirect(url_for('inventory'))

    product = ET.Element("product")
    ET.SubElement(product, "id").text = product_id
    ET.SubElement(product, "barCode").text = bar_code
    ET.SubElement(product, "type").text = product_type
    ET.SubElement(product, "name").text = product_name
    ET.SubElement(product, "purchasePrice").text = purchase_price
    ET.SubElement(product, "salePrice").text = sale_price
    ET.SubElement(product, "stock").text = stock
    ET.SubElement(product, "totalPurchasePrice").text = total_purchase_price
    ET.SubElement(product, "totalSalePrice").text = total_sale_price
    ET.SubElement(product, "saleable").text = saleable

    root.append(product)
    tree.write("inventory.xml")

    flash("Product added successfully!", "success")
    return redirect(url_for('inventory'))

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        # Update the product in the XML file
        new_bar_code = request.form['productBarCode']
        new_product_type = request.form['productType']
        new_product_name = request.form['productName']
        new_purchase_price = request.form['purchasePrice']
        new_sale_price = request.form['salePrice']
        new_stock = request.form['stock']
        new_total_purchase_price = str(float(new_purchase_price) * int(new_stock))
        new_total_sale_price = str(float(new_sale_price) * int(new_stock))
        new_saleable = request.form['saleable']

        tree = ET.parse("inventory.xml")
        root = tree.getroot()
        for product in root.findall('product'):
            if product.find('id').text == product_id:
                product.find('barCode').text = new_bar_code
                product.find('type').text = new_product_type
                product.find('name').text = new_product_name
                product.find('purchasePrice').text = new_purchase_price
                product.find('salePrice').text = new_sale_price
                product.find('stock').text = new_stock
                product.find('totalPurchasePrice').text = new_total_purchase_price
                product.find('totalSalePrice').text = new_total_sale_price
                product.find('saleable').text = new_saleable
                break
        tree.write("inventory.xml")

        flash("Product updated successfully!", "success")
        return redirect(url_for('inventory'))

    else:
        # Retrieve the product details and show them in the form
        tree = ET.parse("inventory.xml")
        root = tree.getroot()
        for product in root.findall('product'):
            if product.find('id').text == product_id:
                product_details = {
                    "id": product.find('id').text,
                    "barCode": product.find('barCode').text,
                    "type": product.find('type').text,
                    "name": product.find('name').text,
                    "purchasePrice": product.find('purchasePrice').text,
                    "salePrice": product.find('salePrice').text,
                    "stock": product.find('stock').text,
                    "totalPurchasePrice": product.find('totalPurchasePrice').text,
                    "totalSalePrice": product.find('totalSalePrice').text,
                    "saleable": product.find('saleable').text,
                }
                return render_template('edit_product.html', product=product_details)
        flash("Product not found!", "error")
        return redirect(url_for('inventory'))

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    if os.path.exists("inventory.xml"):
        tree = ET.parse("inventory.xml")
        root = tree.getroot()
        for product in root.findall('product'):
            if product.find('id').text == product_id:
                root.remove(product)
                tree.write("inventory.xml")
                flash("Product deleted successfully!", "success")
                break
    return redirect(url_for('inventory'))

@app.route('/get_product_details/<product_id_or_barcode>', methods=['GET'])
def get_product_details(product_id_or_barcode):
    if os.path.exists("inventory.xml"):
        tree = ET.parse("inventory.xml")
        root = tree.getroot()
        for product in root.findall('product'):
            if product.find('id').text == product_id_or_barcode or product.find('barCode').text == product_id_or_barcode:
                return jsonify({
                    "product_name": product.find('name').text,
                    "sale_price": product.find('salePrice').text
                })
    return jsonify({"error": "Product ID or BarCode does not exist!"})

@app.route('/add_order', methods=['POST'])
def add_order():
    date = request.form['date']
    product_id_or_barcode = request.form['productIdOrBarCode']
    order_qty = int(request.form['orderQty'])
    bill_paid = float(request.form['billPaid'])

    if not os.path.exists("inventory.xml"):
        flash("Inventory is empty!", "error")
        return redirect(url_for('purchases'))

    tree = ET.parse("inventory.xml")
    root = tree.getroot()
    product = None
    for prod in root.findall('product'):
        if prod.find('id').text == product_id_or_barcode or prod.find('barCode').text == product_id_or_barcode:
            product = prod
            break

    if not product:
        flash("Product ID or BarCode does not exist!", "error")
        return redirect(url_for('purchases'))

    product_name = product.find('name').text
    sale_price = float(product.find('salePrice').text)
    stock = int(product.find('stock').text)
    order_amount = order_qty * sale_price
    balance = order_amount - bill_paid

    if order_qty <= 0 or order_qty > stock:
        flash("Order quantity is invalid or exceeds available stock!", "error")
        return redirect(url_for('purchases'))

    if bill_paid <= 0:
        flash("Bill paid cannot be zero!", "error")
        return redirect(url_for('purchases'))

    if bill_paid > order_amount:
        flash("Bill paid cannot exceed the order amount!", "error")
        return redirect(url_for('purchases'))

    # Update inventory
    new_stock = stock - order_qty
    if new_stock == 0:
        root.remove(product)
    else:
        product.find('stock').text = str(new_stock)
        product.find('totalPurchasePrice').text = str(new_stock * float(product.find('purchasePrice').text))
        product.find('totalSalePrice').text = str(new_stock * sale_price)

    tree.write("inventory.xml")

    # Save the order to a file or database as needed
    orders = []
    if os.path.exists("orders.xml"):
        orders_tree = ET.parse("orders.xml")
        orders_root = orders_tree.getroot()
    else:
        orders_root = ET.Element("orders")
        orders_tree = ET.ElementTree(orders_root)

    order = ET.Element("order")
    ET.SubElement(order, "id").text = str(len(orders_root) + 1)  # Assigning a simple ID
    ET.SubElement(order, "date").text = date
    ET.SubElement(order, "product_name").text = product_name
    ET.SubElement(order, "order_qty").text = str(order_qty)
    ET.SubElement(order, "order_amount").text = str(order_amount)
    ET.SubElement(order, "bill_paid").text = str(bill_paid)
    ET.SubElement(order, "balance").text = str(balance)
    orders_root.append(order)
    orders_tree.write("orders.xml")

    flash("Purchase order added successfully!", "success")
    return redirect(url_for('purchases'))

@app.route('/purchases')
def purchases():
    orders = []
    if os.path.exists("orders.xml"):
        tree = ET.parse("orders.xml")
        root = tree.getroot()
        for order_elem in root.findall('order'):
            order = {
                "id": order_elem.find('id').text,
                "date": order_elem.find('date').text,
                "product_name": order_elem.find('product_name').text,
                "order_qty": order_elem.find('order_qty').text,
                "order_amount": order_elem.find('order_amount').text,
                "bill_paid": order_elem.find('bill_paid').text,
                "balance": order_elem.find('balance').text,
            }
            orders.append(order)
    return render_template('purchase.html', orders=orders)

@app.route('/delete_order/<order_id>')
def delete_order(order_id):
    if os.path.exists("orders.xml"):
        tree = ET.parse("orders.xml")
        root = tree.getroot()
        order_found = False
        for order in root.findall('order'):
            if order.find('id').text == order_id:
                root.remove(order)
                tree.write("orders.xml")
                order_found = True
                flash("Order deleted successfully!", "success")
                break
        if not order_found:
            flash("Order ID not found!", "error")
    else:
        flash("Orders file does not exist!", "error")
    return redirect(url_for('purchases'))

if __name__ == '__main__':
    app.run(debug=True)
    
    