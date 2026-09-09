from flask import Blueprint

users_bp = Blueprint('users', __name__)

# Import routes to register them with the blueprint
from users import routes
