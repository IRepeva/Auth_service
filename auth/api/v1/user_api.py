from http import HTTPStatus

from flask import request, jsonify, Blueprint, redirect
from flask_jwt_extended import (
    get_jwt_identity, jwt_required, get_jwt, unset_refresh_cookies
)
from flask_rebar import errors
from user_agents import parse

from api.models import User, LoginHistory
from api.v1.schemas.user_api import (
    user_login_schema, user_profile_schema, login_history_schema
)
from api.v1.utils.other import get_device_type
from api.v1.utils.tokens import get_new_jwt_tokens, add_tokens_to_blocklist
from databases import db
from extensions import rebar

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
registry = rebar.create_handler_registry()

URL_USER_PREFIX = '/user'
URL_USER_PROFILE = f'{URL_USER_PREFIX}/profile'
DEFAULT_PAGE_SIZE = 50
tag = 'user'


def login_user(user, user_agent):
    user_agent = parse(user_agent)
    device_type = get_device_type(user_agent)
    user_history = LoginHistory(
        user=user.id,
        user_agent=str(user_agent),
        device_type=device_type
    )
    db.session.add(user_history)
    db.session.commit()

    return get_new_jwt_tokens(user)


def add_new_user(email, password):
    new_user = User(
        email=email,
        password=User.get_hashed_password(password),
    )
    db.session.add(new_user)
    db.session.commit()

    return new_user


@registry.handles(
    rule=f'{URL_USER_PREFIX}/register',
    method='POST',
    tags=[tag],
    request_body_schema=user_login_schema
)
def register():
    """User registration"""
    data = user_login_schema.load(request.get_json())

    user = db.session.query(User).filter(User.email == data['email']).first()
    if user:
        raise errors.BadRequest(msg='A user with this email already exists')

    add_new_user(data['email'], data['password'])

    return {'success': True}, HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USER_PREFIX}/login',
    method='POST',
    tags=[tag],
    request_body_schema=user_login_schema,
)
def login():
    """User login"""
    data = user_login_schema.load(request.get_json())

    user = db.session.query(User).filter(User.email == data['email']).first()
    if not user or not user.check_password(data['password']):
        raise errors.BadRequest('Wrong email or password')

    response = login_user(user, request.headers['User-Agent'])

    return response, HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USER_PREFIX}/logout',
    method='DELETE',
    tags=[tag],
)
@jwt_required(refresh=True)
def logout():
    """User logout"""
    jwt = get_jwt()
    add_tokens_to_blocklist(jwt)

    response = jsonify({"msg": "Successfully logged out"})
    unset_refresh_cookies(response)

    return response, HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USER_PREFIX}/refresh',
    method='POST',
    tags=[tag],
)
@jwt_required(refresh=True)
def refresh():
    """Get a new pair of JWT tokens"""
    jwt = get_jwt()
    add_tokens_to_blocklist(jwt)

    user_id = jwt['sub'].get('user_id')
    user = db.session.query(User).filter(User.id == user_id).first()

    response = get_new_jwt_tokens(user)

    return response, HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USER_PROFILE}',
    method='GET',
    tags=[tag],
    response_body_schema=user_profile_schema
)
@jwt_required()
def user_get_profile():
    """Get user profile"""
    user_id = get_jwt_identity().get('user_id')
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise errors.NotFound(f'User not found')

    return user_profile_schema.dump(user)


@registry.handles(
    rule=f'{URL_USER_PROFILE}',
    request_body_schema=user_profile_schema,
    tags=[tag],
    method='PUT'
)
@jwt_required()
def user_edit_profile():
    """Edit user profile"""
    user_id = get_jwt_identity().get('user_id')
    user = db.session.query(User).filter(User.id == user_id)
    if not user.first():
        raise errors.NotFound(f'User not found')

    data = user_profile_schema.load(request.get_json())
    user.update(data, synchronize_session=False)
    db.session.commit()

    return jsonify({"msg": f"User was updated"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USER_PROFILE}',
    tags=[tag],
    method='DELETE'
)
@jwt_required(refresh=True)
def user_delete_profile():
    """Delete user profile"""
    user_id = get_jwt_identity().get('user_id')
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise errors.NotFound(f'User not found')

    db.session.delete(user)
    db.session.commit()

    return redirect(f'{URL_USER_PREFIX}/logout', code=307)


@registry.handles(
    rule=f'{URL_USER_PREFIX}/login_history',
    method='GET',
    tags=[tag],
    response_body_schema=login_history_schema
)
@jwt_required()
def user_get_login_history():
    """Get user login history"""
    query_args = request.args
    page_num, page_size = query_args.get("page"), query_args.get("page_size")
    page_num = 1 if not page_num else page_num
    page_size = DEFAULT_PAGE_SIZE if not page_size else page_size

    user_id = get_jwt_identity().get('user_id')
    login_history = LoginHistory.query.filter_by(
        user=user_id
    ).paginate(
        page=page_num,
        per_page=page_size
    ).items

    return login_history_schema.dump(login_history)
