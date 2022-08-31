from http import HTTPStatus

from api.v1.utils.tokens import get_cache_keys
from databases import cache


def check_tokens_in_blocklist(refresh_jwt):
    refresh_key, access_key = get_cache_keys(refresh_jwt)
    assert cache.get(refresh_key) and cache.get(access_key)


def check_unauthorized(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    return resp


def check_unprocessable_entity(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    return resp


def check_ok(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.OK
    return resp


def check_not_found(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.NOT_FOUND
    return resp


def check_bad_request(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    return resp


def check_method_not_allowed(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    return resp


def check_forbidden(client, url, method, **kwargs):
    resp = getattr(client, method)(url, **kwargs)
    assert resp.status_code == HTTPStatus.FORBIDDEN
    return resp

