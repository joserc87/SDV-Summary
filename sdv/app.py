import os

from flask import Flask

from config import config
from .blueprints import blueprints
from .models import db

__all__ = ['create_app', 'legacy_location']


def register_blueprints(app):
    for blueprint, prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)


def register_extensions(app):
    db.init_app(app)


def register_filters(app):
    pass


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('SDV_APP_SETTINGS', 'production')
    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)
    register_filters(app)

    # Enable jinja2 extensions
    app.jinja_env.add_extension('jinja2.ext.do')

    return app
