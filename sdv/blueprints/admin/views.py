from flask import render_template
from flask_security import login_required, roles_required

from . import admin

@admin.route('/')
@login_required
@roles_required('admin')
def index():
    return render_template('admin/admin.html')