import os
import flask
from flask_mako import MakoTemplates
from . import config
from . import model
from .model import db
from .fernet import fernet
from .auth import login_manager


def create_minimal_app(config_class=None, config_dict=None):
    app = flask.Flask(__name__)
    app.config.from_object(config.DefaultConfig)
    key = os.environ.get('FLASK_SECRET_KEY')
    if key:
        app.config['SECRET_KEY'] = key

    if config_class:
        app.config.from_object(config_class)

    if config_dict:
        app.config.from_mapping(config_dict)

    db.init_app(app)
    fernet.init_app(app)
    login_manager.init_app(app)

    return app


def register_extensions(app):
    MakoTemplates(app)

    from .admin import admin

    admin.init_app(app)


def create_app(config_class=None, config_dict=None):
    app = create_minimal_app(config_class, config_dict)
    register_extensions(app)

    return app


__all__ = ('admin', 'app', 'config', 'model', 'db')
