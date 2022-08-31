import sys

from flask import Flask


sys.path.append('.')

from commands import create_superuser
from core.settings import BASE_CONFIG
from extensions import migrate, jwt, ma, bcrypt, rebar

from databases import init_db, db
from api.v1.admin_api import admin_blueprint
from api.v1.user_api import user_blueprint
from api import models


def init_extensions(app: Flask):
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    ma.init_app(app)
    bcrypt.init_app(app)
    rebar.init_app(app)


def register_blueprints(app: Flask):
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)


def add_commands(app):
    app.cli.add_command(create_superuser)


def create_app(config=BASE_CONFIG):
    app = Flask(__name__)
    app.config.from_object(config)

    init_db(app)
    init_extensions(app)
    add_commands(app)
    register_blueprints(app)

    return app


app = create_app()
