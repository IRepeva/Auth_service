import uuid
from datetime import datetime

import bcrypt
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from databases import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    login_history = db.relationship(
        'LoginHistory', backref='users', cascade='delete'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def get_hashed_password(cls, password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed_password.decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def get_token_payload(self):
        roles = [role.name for role in self.get_user_roles()]
        return {'user_id': self.id, 'roles': roles}

    def get_user_roles(self):
        return db.session.query(
            Role
        ).join(
            UserRole,
            UserRole.role == Role.id
        ).join(
            User,
            UserRole.user == self.id
        ).all()

    def update_user_roles(self, role_ids: list):
        role_ids = set(role_ids)
        current = db.session.query(
            UserRole
        ).join(
            Role,
            Role.id == UserRole.role
        ).filter(
            UserRole.user == self.id,
        ).all()

        for user_role in current:
            if user_role.role not in role_ids:
                db.session.delete(user_role)
                continue
            role_ids.remove(user_role.role)

        for new_role in role_ids:
            db.session.add(UserRole(user=self.id, role=new_role))

        db.session.commit()


class LoginHistory(db.Model):
    __tablename__ = 'login_history'
    __table_args__ = (
        UniqueConstraint('id', 'device_type'),
        {'postgresql_partition_by': 'LIST (device_type)'}
    )
    DEVICE_TYPES = {
        'mobile': 'mobile',
        'pc': 'pc',
        'tablet': 'tablet',
        'other': 'other'
    }

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(
        UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False
    )
    login_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    device_type = db.Column(db.String, primary_key=True)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)

    def get_role_users(self):
        return db.session.query(
            User
        ).join(
            UserRole,
            UserRole.user == User.id
        ).join(
            Role,
            UserRole.role == self.id
        ).all()


class UserRole(db.Model):
    __tablename__ = 'user_role'
    __table_args__ = (UniqueConstraint('user', 'role'),)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(
        UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False
    )
    role = db.Column(
        UUID(as_uuid=True),
        ForeignKey(Role.id, ondelete="CASCADE"),
        nullable=False
    )
