"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2022-09-02 18:29:27.390035

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('login_history',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('login_date', sa.DateTime(), nullable=False),
    sa.Column('user_agent', sa.String(), nullable=False),
    sa.Column('device_type', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'device_type'),
    sa.UniqueConstraint('id', 'device_type'),
    postgresql_partition_by='LIST (device_type)'
    )

    op.execute("CREATE TABLE IF NOT EXISTS login_history_mobile PARTITION OF login_history FOR VALUES IN ('mobile');")
    op.execute("CREATE TABLE IF NOT EXISTS login_history_pc PARTITION OF login_history FOR VALUES IN ('pc');")
    op.execute("CREATE TABLE IF NOT EXISTS login_history_tablet PARTITION OF login_history FOR VALUES IN ('tablet');")
    op.execute("CREATE TABLE IF NOT EXISTS login_history_other PARTITION OF login_history FOR VALUES IN ('other');")

    op.create_table('social_account',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('social_user_id', sa.Text(), nullable=False),
    sa.Column('social_service', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_user_id', 'social_service', name='social_pk')
    )
    op.create_table('user_role',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('role', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['role'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user', 'role')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_role')
    op.drop_table('social_account')
    op.drop_table('login_history')
    op.drop_table('login_history_mobile')
    op.drop_table('login_history_pc')
    op.drop_table('login_history_tablet')
    op.drop_table('login_history_other')
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
