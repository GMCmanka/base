from flask import Blueprint

roles_bp = Blueprint('roles', __name__, url_prefix='/role')

# Import routes to register them with the blueprint
from roles import routes
