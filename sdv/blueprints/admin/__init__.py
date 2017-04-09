from flask import Blueprint
from flask_security import roles_required

admin = Blueprint('admin', __name__,
                  template_folder='templates/admin')

from .views import *  # noqa