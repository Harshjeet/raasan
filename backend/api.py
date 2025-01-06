from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .models import Product
from . import db

api = Blueprint('api', __name__)

@api.route('/products', methods=['GET'])
def get_products():
    """Fetch all products."""
    products = Product.query.all()
    product_list = [{"id": p.id, "name": p.name, "price": p.price, "description": p.description} for p in products]
    return jsonify(product_list)

@api.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    """Add a new product (requires authentication)."""
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')

    new_product = Product(name=name, price=price, description=description)

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'product_id': new_product.id})

@api.route('/product/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update an existing product (requires authentication)."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.description = data.get('description', product.description)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

