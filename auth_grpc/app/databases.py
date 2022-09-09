import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.settings import settings

db = SQLAlchemy()
cache = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def configure_db(app: Flask):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRES_URL

    db.init_app(app)
