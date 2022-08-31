import json

from auth.api.check_functions import (
    check_unauthorized, check_unprocessable_entity, check_ok, check_forbidden,
    check_bad_request, check_not_found
)
from auth.conftest import (
    BASE_ID, SUPERUSER_ID, create_user_with_roles, HEADERS_WITH_BAD_TOKEN,
    SOME_ID, db_add, BASE_EMAIL, BASE_PASSWORD
)

from api.models import Role, User, LoginHistory
from api.v1.admin_api import URL_ROLE_PREFIX, URL_USERS_PREFIX
from api.v1.utils.auth_decorators import SUPERUSER
from databases import db

URL_ADMIN_PROFILE = f'{URL_USERS_PREFIX}/{BASE_ID}'


def test_roles(client, get_access_token):
    method = 'get'

    # no token
    check_unauthorized(client, URL_ROLE_PREFIX, method)

    # bad token
    check_unprocessable_entity(
        client, URL_ROLE_PREFIX, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, URL_ROLE_PREFIX, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(
        email='Dipsy@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, URL_ROLE_PREFIX, method,
        headers={'Authorization': 'Bearer ' + access_token}

    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    resp = check_ok(
        client, URL_ROLE_PREFIX, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    assert len(json.loads(resp.data)) == 2  # superuser, admin

    # ok (internal user)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    resp = check_ok(
        client, URL_ROLE_PREFIX, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    assert len(json.loads(resp.data)) == 3  # admin, superuser, internal


def test_get_role(client, get_access_token):
    super_role = db.session.query(Role).filter(Role.name == SUPERUSER).first()
    url = URL_ROLE_PREFIX + f'/{super_role.id}'
    method = 'get'

    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(
        email='Dipsy@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}

    )

    # no such role
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ROLE_PREFIX + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (internal user)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )


def test_edit_role(client, get_access_token):
    new_role = db_add(Role(name='WhyAmIHere'))
    url = URL_ROLE_PREFIX + f'/{new_role.id}'
    body = {"name": "ForNoReason"}
    method = 'put'

    # no token
    check_unauthorized(client, url, method, json=body)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN,
        json=body
    )

    # wrong body
    access_token = get_access_token()
    check_bad_request(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={'fake': 'news'}
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # no such role
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ROLE_PREFIX + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )
    role = db.session.query(Role).filter(Role.id == new_role.id).first()
    assert role.name == body['name']

    # ok (admin user)
    new_user = create_user_with_roles(
        email='Dipsy@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    another_body = {"name": "sunBaby"}
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=another_body
    )
    role = db.session.query(Role).filter(Role.id == new_role.id).first()
    assert role.name == another_body['name']

    # ok (manager user)
    new_user = create_user_with_roles(
        email='Po@teletubbies.freaky',
        password='BigHugs',
        roles='manager'
    )
    access_token = get_access_token(new_user.id)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )
    role = db.session.query(Role).filter(Role.id == new_role.id).first()
    assert role.name == body['name']


def test_delete_role(client, get_access_token):
    new_role = db_add(Role(name='IAmYourFather'))
    url = URL_ROLE_PREFIX + f'/{new_role.id}'
    method = 'delete'

    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN,
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with only one role)
    new_user = create_user_with_roles(roles='admin')
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # no such role
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ROLE_PREFIX + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    role = db.session.query(Role).filter(Role.id == new_role.id).first()
    assert role is None

    # ok (user with both admin and manager roles)
    new_role = db_add(Role(name='IAmYourFather'))
    url = URL_ROLE_PREFIX + f'/{new_role.id}'

    new_user = create_user_with_roles(
        email='Tinky-Winky@teletubbies.freaky',
        password='BigHugs',
        roles=['admin', 'manager']
    )
    access_token = get_access_token(new_user.id)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    role = db.session.query(Role).filter(Role.id == new_role.id).first()
    assert role is None


def test_roles_create(client, get_access_token):
    url = URL_ROLE_PREFIX + '/create'
    body = {"name": "teletubby"}
    method = 'post'

    # no token
    check_unauthorized(client, url, method, json=body)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN,
        json=body
    )

    # wrong body
    access_token = get_access_token()
    check_bad_request(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={'fake': 'news'}
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # duplicate role
    access_token = get_access_token(SUPERUSER_ID)
    check_bad_request(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={"name": SUPERUSER}
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )
    # superuser, internal, teletubby
    roles = db.session.query(Role).all()
    assert len(roles) == 3

    # ok (admin user)
    new_user = create_user_with_roles(
        email='Dipsy@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={"name": "sunBaby"}
    )
    # superuser, internal, teletubby, admin, sunBaby
    roles = db.session.query(Role).all()
    assert len(roles) == 5

    # ok (manager user)
    new_user = create_user_with_roles(
        email='Po@teletubbies.freaky',
        password='BigHugs',
        roles='manager'
    )
    access_token = get_access_token(new_user.id)
    check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={"name": "SunBaby"}
    )
    # superuser, internal, teletubby, admin, sunBaby, manager, SunBaby
    roles = db.session.query(Role).all()
    assert len(roles) == 7


def test_admin_get_profile(client, get_access_token):
    method = 'get'

    # no token
    check_unauthorized(client, URL_ADMIN_PROFILE, method)

    # bad token
    check_unprocessable_entity(
        client, URL_ADMIN_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(
        email='Po@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}

    )

    # no such user
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ADMIN_PROFILE + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (internal user)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )


def test_admin_edit_profile(client, get_access_token):
    body = {'email': BASE_EMAIL, "username": "Tinky-Winky"}
    method = 'put'

    # no token
    check_unauthorized(client, URL_ADMIN_PROFILE, method, json=body)

    # bad token
    check_unprocessable_entity(
        client, URL_ADMIN_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN,
        json=body
    )

    # wrong body
    access_token = get_access_token()
    check_bad_request(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json={'fake': 'news'}
    )

    # no such user
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ADMIN_PROFILE + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # forbidden (user with only one role)
    new_user = create_user_with_roles(
        email='Laa-Laa@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=body
    )
    user = db.session.query(User).filter(User.id == BASE_ID).first()
    assert user.username == body['username']

    # ok (user with both admin and manager roles)
    new_user = create_user_with_roles(
        email='Tinky-Winky@teletubbies.freaky',
        password='BigHugs',
        roles=['admin', 'manager']
    )
    access_token = get_access_token(new_user.id)
    another_body = {'email': BASE_EMAIL, 'username': 'Po'}
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token},
        json=another_body
    )
    user = db.session.query(User).filter(User.id == BASE_ID).first()
    assert user.username == another_body['username']


def test_admin_delete_profile(client, get_access_token, create_base_user):
    method = 'delete'

    # no token
    check_unauthorized(client, URL_ADMIN_PROFILE, method)

    # bad token
    check_unprocessable_entity(
        client, URL_ADMIN_PROFILE, method,
        headers=HEADERS_WITH_BAD_TOKEN,
    )

    # no such user
    access_token = get_access_token(SUPERUSER_ID)
    check_not_found(
        client, URL_ADMIN_PROFILE + f'/{SOME_ID}', method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with only one role)
    new_user = create_user_with_roles(roles='admin')
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (superuser)
    access_token = get_access_token(SUPERUSER_ID)
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    user = db.session.query(User).filter(User.id == BASE_ID).first()
    assert user is None

    # ok (user with both admin and manager roles)
    hashed_password = User.get_hashed_password(BASE_PASSWORD)
    db_add(User(id=BASE_ID, email=BASE_EMAIL, password=hashed_password))

    new_user = create_user_with_roles(
        email='Tinky-Winky@teletubbies.freaky',
        password='BigHugs',
        roles=['admin', 'manager']
    )
    access_token = get_access_token(new_user.id)
    check_ok(
        client, URL_ADMIN_PROFILE, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    user = db.session.query(User).filter(User.id == BASE_ID).first()
    assert user is None


def test_get_login_history(client, get_access_token):
    url = URL_ADMIN_PROFILE + '/login_history'
    method = 'get'

    # no token
    check_unauthorized(client, url, method)

    # bad token
    check_unprocessable_entity(
        client, url, method,
        headers=HEADERS_WITH_BAD_TOKEN
    )

    # forbidden (user without role)
    access_token = get_access_token()
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # forbidden (user with inappropriate role)
    new_user = create_user_with_roles(
        email='Po@teletubbies.freaky',
        password='BigHugs',
        roles='admin'
    )
    access_token = get_access_token(new_user.id)
    check_forbidden(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )

    # ok (superuser)
    db_add(LoginHistory(user=BASE_ID, user_agent='007'))
    access_token = get_access_token(SUPERUSER_ID)
    resp = check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    assert len(json.loads(resp.data)) == 1

    # ok (internal user)
    db_add(LoginHistory(user=BASE_ID, user_agent='008'))
    db_add(LoginHistory(user=BASE_ID, user_agent='009'))

    new_user = create_user_with_roles(roles='internal')
    access_token = get_access_token(new_user.id)
    resp = check_ok(
        client, url, method,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    assert len(json.loads(resp.data)) == 3
