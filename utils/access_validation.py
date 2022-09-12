import jwt

SUPERUSER = 'superuser'


def get_blocklist_key(jti: str, user_id: str) -> str:
    return user_id + ':' + jti


def is_access_token_in_blocklist(jwt_payload, cache):
    access_jti = jwt_payload['jti']
    user_id = jwt_payload['sub']['user_id']

    cache_key = get_blocklist_key(access_jti, user_id)
    return cache.get(cache_key)


async def async_is_access_token_in_blocklist(jwt_payload, cache):
    access_jti = jwt_payload['jti']
    user_id = jwt_payload['sub']['user_id']

    cache_key = get_blocklist_key(access_jti, user_id)
    return await cache.get(cache_key)


def get_token_from_request(**kwargs):
    if request := kwargs.get('request'):
        if token := request.headers.get('Authorization'):
            try:
                return True, token.split(' ')[1]
            except IndexError:
                return False, 'Wrong token format'
        return False, 'No access token in Headers'
    return False, 'No request object provided for the endpoint'


def is_authorized(secret_key, cache, **kwargs):
    status, response = get_token_from_request(**kwargs)
    if status:
        return is_token_valid(response, secret_key, cache)

    return False, response


async def async_is_authorized(secret_key, cache, **kwargs):
    status, response = get_token_from_request(**kwargs)
    if status:
        return await async_is_token_valid(response, secret_key, cache)

    return False, response


def is_token_valid(token, secret_key, cache):
    try:
        print(f'TOKEN: {token}, class: {type(token)}')
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except Exception as e:
        return False, str(e)

    if is_access_token_in_blocklist(payload, cache):
        return False, 'Token is in the blocklist'

    return True, payload


async def async_is_token_valid(token, secret_key, cache):
    try:
        print(f'TOKEN: {token}, class: {type(token)}')
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except Exception as e:
        return False, str(e)

    if await async_is_access_token_in_blocklist(payload, cache):
        return False, 'Token is in the blocklist'

    return True, payload


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


def is_allowed(user_roles, or_, and_, roles):
    if SUPERUSER in user_roles:
        return True

    or_roles, and_roles = prepare_roles(or_, and_, roles)
    if (
        check_or(or_roles, user_roles) if or_roles else True
        and check_and(and_roles, user_roles) if and_roles else True
    ):
        return True

    return False
