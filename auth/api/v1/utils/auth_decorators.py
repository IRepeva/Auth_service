from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, jwt_required

SUPERUSER = 'superuser'


def check_or(or_roles, user_roles):
    return any(arg in user_roles for arg in or_roles)


def check_and(and_roles, user_roles):
    return all(arg in user_roles for arg in and_roles)


def prepare_roles(or_, and_, roles):
    if not or_:
        or_ = []
    or_roles = [or_] if not isinstance(or_, (list, tuple)) else or_

    if not and_:
        and_ = []
    and_roles = [and_] if not isinstance(and_, (list, tuple)) else and_

    if roles:
        other_roles = [roles] if not isinstance(roles, (list, tuple)) else roles
        or_roles.extend(other_roles)

    return or_roles, and_roles


def has_access(*roles, or_=None, and_=None):
    def wrapper(func):
        @jwt_required()
        @wraps(func)
        def decorator(*args, **kwargs):
            user_roles = get_jwt_identity()['roles']
            if SUPERUSER in user_roles:
                return func(*args, **kwargs)

            or_roles, and_roles = prepare_roles(or_, and_, roles)
            if (
                    check_or(or_roles, user_roles) if or_roles else True
                    and check_and(and_roles, user_roles) if and_roles else True
            ):
                return func(*args, **kwargs)

            return {"msg": f"Access forbidden"}, HTTPStatus.FORBIDDEN

        return decorator

    return wrapper
