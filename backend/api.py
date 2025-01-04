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
