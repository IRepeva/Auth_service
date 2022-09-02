import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.settings import db_settings, jwt_settings

db = SQLAlchemy()
cache = redis.Redis(host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT)

ACCESS_TOKEN_EXPIRE = jwt_settings.JWT_ACCESS_TOKEN_EXPIRES
REFRESH_TOKEN_EXPIRE = jwt_settings.JWT_REFRESH_TOKEN_EXPIRES


def configure_db(app: Flask):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = db_settings.SQLALCHEMY_DATABASE_URI

    db.init_app(app)
