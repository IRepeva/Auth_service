from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, jwt_required

from utils.access_validation import is_allowed


def has_access(*roles, or_=None, and_=None):
    def wrapper(func):
        @jwt_required()
        @wraps(func)
        def decorator(*args, **kwargs):
            user_roles = get_jwt_identity()['roles']
            if is_allowed(user_roles, or_, and_, roles):
                return func(*args, **kwargs)

            return {"msg": f"Access forbidden"}, HTTPStatus.FORBIDDEN

        return decorator

    return wrapper
