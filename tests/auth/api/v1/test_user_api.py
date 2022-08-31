import json

from auth.api.check_functions import (
    check_unauthorized, check_unprocessable_entity, check_ok, check_bad_request,
    check_method_not_allowed, check_tokens_in_blocklist
)
from auth.conftest import (
    BASE_EMAIL, BASE_PASSWORD, BASE_ID, HEADERS_WITH_BAD_TOKEN, db_add
)
from flask_jwt_extended import get_jwt

from api.models import User, LoginHistory
from api.v1.user_api import URL_USER_PROFILE, URL_USER_PREFIX
from databases import db

USERNAME = 'Corvax'
NEW_EMAIL = 'princess@sylvia.bbc'


def test_get_profile(client, get_access_token):
    method = 'get'
    # no token
    check_unauthorized(client, URL_USER_PROFILE, method)

    # bad token
    check_unprocessable_entity(
        client, URL_USER_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # ok
    access_token = get_access_token()
    headers = {'Authorization': 'Bearer ' + access_token}
    resp = check_ok(client, URL_USER_PROFILE, method, headers=headers)
    assert json.loads(resp.data)['email'] == BASE_EMAIL


def test_edit_profile(client, get_access_token):
    body = {'email': BASE_EMAIL, 'username': USERNAME}
    method = 'put'

    # no token
    check_unauthorized(client, URL_USER_PROFILE, method, json=body)

    # bad token
    check_unprocessable_entity(
        client, URL_USER_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN,
        json=body
    )

    # No email
    access_token = get_access_token()
    check_bad_request(
        client, URL_USER_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={'username': USERNAME}
    )

    # ok
    check_ok(
        client, URL_USER_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )
    upd_user = db.session.query(User).filter(User.email == BASE_EMAIL).first()
    assert upd_user.username == USERNAME


def test_delete_profile(client, get_refresh_token):
    method = 'delete'

    # no token
    check_unauthorized(client, URL_USER_PROFILE, method)

    # bad token
    check_unprocessable_entity(
        client, URL_USER_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # ok
    refresh_token = get_refresh_token()
    client.set_cookie('localhost', 'refresh_token_cookie', refresh_token)
    check_ok(
        client, URL_USER_PROFILE, method,
        follow_redirects=True
    )
    del_user = db.session.query(User).filter(User.email == BASE_EMAIL).first()
    assert del_user is None

    check_tokens_in_blocklist(get_jwt())


def test_get_login_history(client, get_access_token):
    url = URL_USER_PREFIX + '/login_history'
    method = 'get'
    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # ok
    db_add(LoginHistory(user=BASE_ID, user_agent='007'))
    db_add(LoginHistory(user=BASE_ID, user_agent='008'))
    db_add(LoginHistory(user=BASE_ID, user_agent='009'))
    access_token = get_access_token()
    headers = {'Authorization': 'Bearer ' + access_token}
    resp = check_ok(client, url, method, headers=headers)
    assert len(json.loads(resp.data)) == 3


def test_register(client):
    url = URL_USER_PREFIX + '/register'
    method = 'post'

    # user exists
    check_bad_request(
        client, url, method,
        json={
            'email': BASE_EMAIL,
            'password': BASE_PASSWORD,
            'password_conf': BASE_PASSWORD
        }
    )

    # passwords don't match
    check_bad_request(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD,
            'password_conf': BASE_PASSWORD + 'wrong'
        })

    # password is too short
    check_bad_request(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': 'short',
            'password_conf': 'short'
        })

    # get method is not allowed
    check_method_not_allowed(
        client, url, 'get',
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD,
            'password_conf': BASE_PASSWORD
        })

    # ok
    check_ok(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD,
            'password_conf': BASE_PASSWORD
        })
    new_user = db.session.query(User).filter(User.email == NEW_EMAIL).first()
    assert new_user is not None


def test_login(client):
    url = URL_USER_PREFIX + '/login'
    method = 'post'

    # user doesn't exist
    check_bad_request(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD
        }
    )

    # wrong password
    check_bad_request(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD + 'wrong'
        })

    # wrong body
    check_bad_request(
        client, url, method,
        json={
            'email': NEW_EMAIL,
            'password': BASE_PASSWORD,
            'i_want_to_be_here': 'but should not :('
        })

    # get method is not allowed
    check_method_not_allowed(
        client, url, 'get',
        json={
            'email': BASE_EMAIL,
            'password': BASE_PASSWORD,
        })

    # ok
    resp = check_ok(
        client, url, method,
        json={
            'email': BASE_EMAIL,
            'password': BASE_PASSWORD,
        })
    assert 'access_token' in json.loads(resp.data)
    assert 'refresh_token' in json.loads(resp.data)

    user_login_history = db.session.query(
        LoginHistory
    ).filter(
        LoginHistory.user == BASE_ID
    ).first()

    assert user_login_history is not None


def test_logout(client, get_refresh_token):
    url = URL_USER_PREFIX + '/logout'
    method = 'delete'

    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # get method is not allowed
    check_method_not_allowed(client, url, 'get')

    # ok
    refresh_token = get_refresh_token()
    client.set_cookie('localhost', 'refresh_token_cookie', refresh_token)
    check_ok(client, url, method)

    check_tokens_in_blocklist(get_jwt())


def test_refresh(client, get_refresh_token):
    url = URL_USER_PREFIX + '/refresh'
    method = 'post'

    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # get method is not allowed
    check_method_not_allowed(client, url, 'get')

    # ok
    refresh_token = get_refresh_token()
    client.set_cookie('localhost', 'refresh_token_cookie', refresh_token)

    resp = check_ok(client, url, method)
    assert 'access_token' in json.loads(resp.data)
    assert 'refresh_token' in json.loads(resp.data)

    check_tokens_in_blocklist(get_jwt())
