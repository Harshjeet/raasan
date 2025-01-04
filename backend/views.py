from flask import Blueprint, render_template, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Home route."""
    return jsonify({"message": "Welcome to Flask-VueJS Backend!"})

@main.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "OK"})
