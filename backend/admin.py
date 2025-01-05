from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Product, Category
from . import db

admin = Blueprint('admin', __name__)

def is_admin(user_id):
    """Check if the user is an admin."""
    user = User.query.get(user_id)
    return user and user.role == "admin"

# -----------------------------------
# CRUD Operations for Categories
# -----------------------------------
@admin.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all categories."""
    categories = Category.query.all()
    category_list = [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
    return jsonify(category_list)

@admin.route('/category', methods=['POST'])
@jwt_required()
def add_category():
    """Add a new category (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    return jsonify({'message': 'Category added successfully', 'category_id': category.id})

@admin.route('/category/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update an existing category (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    category.name = data.get('name', category.name)
    category.description = data.get('description', category.description)

    db.session.commit()
    return jsonify({'message': 'Category updated successfully'})

@admin.route('/category/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category (Admin Only)."""
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized'}), 403

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})

# -----------------------------------
# CRUD Operations for Products
# -----------------------------------
@admin.route('/products', methods=['GET'])
def get_products():
    """Get all products."""
    products = Product.query.all()
    product_list = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "category_id": p.category_id} for p in products]
    return jsonify(product_list)

@admin.route('/product', methods=['POST'])
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

@admin.route('/product/<int:product_id>', methods=['PUT'])
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

@admin.route('/product/<int:product_id>', methods=['DELETE'])
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
