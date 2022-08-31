from flask import jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, set_refresh_cookies, get_jti
)

from databases import (
    cache, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
)
from extensions import jwt


def get_info_from_refresh_jwt(refresh_jwt):
    refresh_jti = refresh_jwt['jti']
    access_jti = refresh_jwt['sub']['access_jti']
    user_id = refresh_jwt['sub']['user_id']
    return refresh_jti, access_jti, user_id


def get_new_jwt_tokens(user):
    identity = user.get_token_payload()
    access_token = create_access_token(identity=identity)

    identity.update({'access_jti': get_jti(access_token)})
    refresh_token = create_refresh_token(identity=identity)

    response = jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })
    set_refresh_cookies(response, refresh_token)

    return response


@jwt.token_in_blocklist_loader
def is_in_blocklist(jwt_header, jwt_payload: dict) -> bool:
    if jwt_payload['type'] == 'refresh':
        refresh_key, access_key = get_cache_keys(jwt_payload)
        return cache.get(refresh_key) or cache.get(access_key)

    access_jti = jwt_payload['jti']
    user_id = jwt_payload['sub']['user_id']

    cache_key = get_blocklist_key(access_jti, user_id)
    return cache.get(cache_key)


def get_cache_keys(refresh_jwt):
    refresh_jti, access_jti, user_id = get_info_from_refresh_jwt(refresh_jwt)

    refresh_key = get_blocklist_key(refresh_jti, user_id)
    access_key = get_blocklist_key(access_jti, user_id)
    return refresh_key, access_key


def add_tokens_to_blocklist(refresh_jwt: dict):
    refresh_key, access_key = get_cache_keys(refresh_jwt)
    cache.setex(refresh_key, REFRESH_TOKEN_EXPIRE, 'True')
    cache.setex(access_key, ACCESS_TOKEN_EXPIRE, 'True')


def get_blocklist_key(jti: str, user_id: str) -> str:
    return user_id + ':' + jti
