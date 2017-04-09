from .admin import admin as admin_blueprint
from .api import api as api_blueprint
from .frontend import frontend as frontend_blueprint

blueprints = [
    (admin_blueprint, '/admin/'),
    (api_blueprint, '/api/'),
    (frontend_blueprint, '')
]