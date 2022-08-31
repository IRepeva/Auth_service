from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_rebar import errors

from api.v1.schemas.user_api import login_history_schema
from api.v1.utils.auth_decorators import has_access
from api.models import User, Role, LoginHistory
from api.v1.schemas.admin_api import (
    roles_schema, user_schema_with_roles, put_admin_profile_schema,
    role_schema, role_schema_with_users, base_admin_profile_schema
)
from api.v1.user_api import registry, DEFAULT_PAGE_SIZE
from databases import db

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')
URL_ADMIN_PREFIX = '/admin'
URL_ROLE_PREFIX = URL_ADMIN_PREFIX + '/roles'
URL_USERS_PREFIX = URL_ADMIN_PREFIX + '/users'
tag = 'admin'


@registry.handles(
    rule=f'{URL_ROLE_PREFIX}',
    method='GET',
    tags=[tag],
    response_body_schema={
        200: roles_schema,
        403: None
    }
)
@has_access('internal')
def get_roles():
    """Get all roles"""
    roles = db.session.query(Role).all()
    return roles_schema.dump(roles)


@registry.handles(
    rule=f'{URL_ROLE_PREFIX}/create',
    tags=[tag],
    method='POST',
    request_body_schema=role_schema
)
@has_access('admin', 'manager')
def admin_create_role():
    """Create new role"""
    data = role_schema.load(request.get_json())
    role = db.session.query(Role).filter(Role.name == data['name']).first()
    if role:
        raise errors.BadRequest(msg=f'A role with this name already exists')

    db.session.add(Role(name=data['name']))
    db.session.commit()

    return jsonify({"msg": f"Role was created"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_ROLE_PREFIX}/<role_id>',
    tags=[tag],
    method='GET',
    response_body_schema={
        200: role_schema_with_users,
        403: None
    }
)
@has_access('internal')
def admin_get_role(role_id):
    """Get role information"""
    role = db.session.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise errors.NotFound(f'Role not found')

    users = base_admin_profile_schema.dump(role.get_role_users())
    role.users = users

    return role_schema_with_users.dump(role)


@registry.handles(
    rule=f'{URL_ROLE_PREFIX}/<role_id>',
    tags=[tag],
    method='PUT',
    request_body_schema=role_schema
)
@has_access('admin', 'manager')
def admin_edit_role(role_id):
    """Edit role"""
    role = db.session.query(Role).filter(Role.id == role_id)
    if not role.first():
        raise errors.NotFound(f'Role not found')

    data = role_schema.load(request.get_json())
    role.update(data, synchronize_session=False)
    db.session.commit()

    return jsonify({"msg": f"Role was updated"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_ROLE_PREFIX}/<role_id>',
    tags=[tag],
    method='DELETE'
)
@has_access(and_=('admin', 'manager'))
def admin_delete_role(role_id):
    """Delete role"""
    role = db.session.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise errors.NotFound(f'Role not found')

    db.session.delete(role)
    db.session.commit()

    return jsonify({"msg": f"Role {role_id} was deleted"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USERS_PREFIX}/<user_id>',
    tags=[tag],
    method='GET',
    response_body_schema={
        200: user_schema_with_roles,
        403: None
    }
)
@has_access('internal')
def admin_get_profile(user_id):
    """Edit user profile"""
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise errors.NotFound(f'User not found')

    roles = roles_schema.dump(user.get_user_roles())
    user.roles = roles

    return user_schema_with_roles.dump(user)


@registry.handles(
    rule=f'{URL_USERS_PREFIX}/<user_id>',
    tags=[tag],
    method='PUT',
    request_body_schema=put_admin_profile_schema,
)
@has_access(and_=('admin', 'manager'))
def admin_edit_profile(user_id):
    """Edit user profile"""
    user = db.session.query(User).filter(User.id == user_id)

    user_item = user.first()
    if not user_item:
        raise errors.NotFound(f'User not found')

    data = put_admin_profile_schema.load(request.get_json())
    if 'roles' in data:
        user_item.update_user_roles(data.pop('roles'))

    user.update(data, synchronize_session=False)
    db.session.commit()

    return jsonify({"msg": f"User profile was updated"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USERS_PREFIX}/<user_id>',
    tags=[tag],
    method='DELETE'
)
@has_access(and_=('admin', 'manager'))
def admin_delete_profile(user_id):
    """Delete user profile"""
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise errors.NotFound(f'User not found')

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": f"User {user_id} was deleted"}), HTTPStatus.OK


@registry.handles(
    rule=f'{URL_USERS_PREFIX}/<user_id>/login_history',
    tags=[tag],
    method='GET',
    response_body_schema={
        200: login_history_schema,
        403: None
    }
)
@has_access('internal')
def admin_get_login_history(user_id):
    """Get user's login_history"""
    query_args = request.args
    page_num, page_size = query_args.get("page"), query_args.get("page_size")
    page_num = 1 if not page_num else page_num
    page_size = DEFAULT_PAGE_SIZE if not page_size else page_size

    login_history = LoginHistory.query.filter_by(
        user=user_id
    ).paginate(
        page=page_num,
        per_page=page_size
    ).items
    return login_history_schema.dump(login_history)
