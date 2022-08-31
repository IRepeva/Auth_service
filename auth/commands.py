import sys

import click

sys.path.append('.')
from api.models import User, Role, UserRole
from api.v1.utils.auth_decorators import SUPERUSER
from databases import db


@click.command('create_superuser')
@click.argument('email')
@click.argument('password')
def create_superuser(email, password):
    hashed_password = User.get_hashed_password(password)
    user_model = User(email=email, password=hashed_password)
    db.session.add(user_model)

    role_model = Role(name=SUPERUSER)
    db.session.add(role_model)

    db.session.flush()

    db.session.add(UserRole(user=user_model.id, role=role_model.id))
    db.session.commit()
