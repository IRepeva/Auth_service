import logging
import uuid
from typing import Union

import pytest
from flask_jwt_extended import create_access_token, get_jti, \
    create_refresh_token

from api.models import User, Role, UserRole
from api.v1.utils.auth_decorators import SUPERUSER
from auth.app import create_app
from core.settings import TEST_CONFIG
from databases import db, cache

logger = logging.getLogger(__name__)

BAD_TOKEN = 'Tinki-Winki.Laa-Laa.Po'
HEADERS_WITH_BAD_TOKEN = {'Authorization': 'Bearer ' + BAD_TOKEN}

BASE_ID = uuid.uuid4()
BASE_EMAIL = 'i@like.clocks'
BASE_PASSWORD = 'IAmMuzzy'

SUPERUSER_ID = uuid.uuid4()
SUPERUSER_EMAIL = 'i@like.lobsters'
SUPERUSER_PASSWORD = 'IAmSuperStar'

SOME_ID = uuid.uuid4()
SOME_EMAIL = 'girl@has_no.name'
SOME_PASSWORD = 'GirlIsNoOne'

MODELS = [
    cls for cls in db.Model.registry._class_registry.values()
    if isinstance(cls, type) and issubclass(cls, db.Model)
]


def tear_down_dbs():
    """
    Delete all data in every table and clear cache
    """
    cache.flushall()
    for model in MODELS:
        db.session.query(model).delete()
    db.session.commit()


@pytest.fixture(scope='session', autouse=True)
def app():
    """
    Create app, db, redis, blueprints for the whole test session
    """
    app = create_app(TEST_CONFIG)
    with app.app_context():
        db.create_all()
        yield app

        db.drop_all()
        db.session.remove()
        cache.flushall()


@pytest.fixture(scope='function', autouse=True)
def client(app):
    """Flask test client for testing api"""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def get_access_token():
    # """Generate access token"""
    def access_token_factory(user_id=BASE_ID):
        user = db.session.query(User).filter(User.id == user_id).first()
        identity = user.get_token_payload()
        return create_access_token(identity=identity)

    return access_token_factory


@pytest.fixture(scope='function')
def get_refresh_token(get_access_token):
    # """Generate refresh token"""
    def refresh_token_factory(user_id=BASE_ID):
        user = db.session.query(User).filter(User.id == user_id).first()
        access_token = get_access_token()
        identity = user.get_token_payload()
        identity.update({'access_jti': get_jti(access_token)})
        return create_refresh_token(identity=identity)

    return refresh_token_factory


def db_add(model):
    """
    Fast method for adding model to the database in tests and return it.
    For example:
        user = db_add(User(email='marylin@manson.rf'))
    """
    db.session.add(model)
    db.session.commit()
    return model


@pytest.fixture(scope="function", autouse=True)
def create_base_user():
    """
    Create and delete base user in each test
    """
    logger.info('Creating base user')
    hashed_password = User.get_hashed_password(BASE_PASSWORD)
    db_add(User(id=BASE_ID, email=BASE_EMAIL, password=hashed_password))

    yield

    logger.info('Deleting base user')
    tear_down_dbs()


@pytest.fixture(scope='function', autouse=True)
def create_superuser():
    """
    Create and delete superuser user in each test
    """
    logger.info('Creating superuser')

    hash_password = User.get_hashed_password(SUPERUSER_PASSWORD)
    db_add(User(id=SUPERUSER_ID, email=SUPERUSER_EMAIL, password=hash_password))
    role = db_add(Role(name=SUPERUSER))
    db_add(UserRole(user=SUPERUSER_ID, role=role.id))

    yield

    logger.info('Deleting superuser')
    tear_down_dbs()


def create_user_with_roles(
        email: str = SOME_EMAIL,
        password: str = SOME_PASSWORD,
        roles: Union[tuple, set, list, str] = None
):
    logger.info(f'Creating user with roles: {roles}')

    hash_password = User.get_hashed_password(password)
    user = db_add(User(email=email, password=hash_password))

    if roles:
        if isinstance(roles, str):
            roles = [roles]

        roles_ids = set()
        for role in roles:
            r = db_add(Role(name=role))
            roles_ids.add(r.id)

        user.update_user_roles(roles_ids)

    return user
