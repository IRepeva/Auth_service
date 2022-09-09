from app.databases import db, configure_db
from app.extensions import migrate, jwt, ma, bcrypt, rebar
from flask import Flask
import app.models


def init_extensions(app: Flask):
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    ma.init_app(app)
    bcrypt.init_app(app)
    rebar.init_app(app)


def create_app():
    app = Flask(__name__)
    app.config.from_object('core.settings.settings')

    configure_db(app)
    init_extensions(app)

    return app


app = create_app()
