from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_rebar import Rebar

jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
bcrypt = Bcrypt()
rebar = Rebar()
