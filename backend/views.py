from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Cart, CartItem, Product, Order, OrderItem, Invoice, Category
from . import db
import uuid

main = Blueprint('main', __name__)

# -----------------------------------
# ROLE CHECK FUNCTION
# -----------------------------------
def is_admin(user_id):
    """Check if the user is an admin."""
    user = User.query.get(user_id)
    return user and user.role == "admin"

# -----------------------------------
# CART MANAGEMENT
# -----------------------------------
@main.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    """Retrieve the user's cart."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.cart:
        return jsonify({'message': 'Cart is empty', 'items': []})

    cart_items = CartItem.query.filter_by(cart_id=user.cart.id).all()
    items = [{"id": item.id, "product_id": item.product_id, "quantity": item.quantity} for item in cart_items]

    return jsonify({'cart_id': user.cart.id, 'items': items})

@main.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add a product to the user's cart."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    if not user.cart:
        user.cart = Cart(user_id=user.id)
        db.session.add(user.cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=user.cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=user.cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Product added to cart'})

@main.route('/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove a product from the user's cart."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.cart:
        return jsonify({'error': 'Cart not found'}), 404

    cart_item = CartItem.query.get(item_id)
    if not cart_item or cart_item.cart_id != user.cart.id:
        return jsonify({'error': 'Item not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})

# -----------------------------------
# ORDER MANAGEMENT
# -----------------------------------
@main.route('/order/place', methods=['POST'])
@jwt_required()
def place_order():
    """Convert the cart into an order."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.cart:
        return jsonify({'error': 'Cart is empty'}), 400

    cart_items = CartItem.query.filter_by(cart_id=user.cart.id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    new_order = Order(user_id=user.id, total_amount=total_amount, status="Pending")
    db.session.add(new_order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(order_item)
        item.product.stock -= item.quantity

    invoice_number = str(uuid.uuid4())[:8]
    invoice = Invoice(order_id=new_order.id, invoice_number=invoice_number, status="Pending")
    db.session.add(invoice)

    CartItem.query.filter_by(cart_id=user.cart.id).delete()
    db.session.commit()

    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.id, 'invoice_number': invoice_number})

@main.route('/order/history', methods=['GET'])
@jwt_required()
def order_history():
    """Retrieve the order history for a user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    orders = Order.query.filter_by(user_id=user.id).all()
    order_list = []
    for order in orders:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        item_list = [{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in items]
        order_list.append({
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "items": item_list
        })

    return jsonify(order_list)

# -----------------------------------
# ADMIN MANAGEMENT (PRODUCTS & CATEGORIES)
# -----------------------------------
@main.route('/admin/products', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products."""
    products = Product.query.all()
    product_list = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "category_id": p.category_id} for p in products]
    return jsonify(product_list)

@main.route('/admin/product', methods=['POST'])
@jwt_required()
def add_product():
    """Add a new product (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock', 0)
    category_id = data.get('category_id')

    if not name or not price or not category_id:
        return jsonify({'error': 'Name, price, and category_id are required'}), 400

    product = Product(name=name, price=price, stock=stock, category_id=category_id)
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'product_id': product.id})

@main.route('/admin/product/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update an existing product (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.category_id = data.get('category_id', product.category_id)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@main.route('/admin/product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
