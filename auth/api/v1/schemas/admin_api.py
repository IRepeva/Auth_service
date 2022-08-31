from marshmallow import fields
from marshmallow.validate import Email

from api.models import User, Role
from extensions import ma


class RoleSchema(ma.SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)

    class Meta:
        model = Role


class RoleSchemaWithUsers(RoleSchema):
    users = fields.List(fields.Dict())


class BaseAdminSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(validate=Email(), required=True)
    date_created = fields.String()

    class Meta:
        model = User
        exclude = ('password',)


class UserSchemaWithRoles(BaseAdminSchema):
    roles = fields.List(fields.Dict())


class PutAdminProfileSchema(BaseAdminSchema):
    roles = fields.List(fields.UUID, default=[])

    class Meta:
        model = User
        exclude = ('password', 'id')


base_admin_profile_schema = BaseAdminSchema(many=True)
user_schema_with_roles = UserSchemaWithRoles()
put_admin_profile_schema = PutAdminProfileSchema()

roles_schema = RoleSchema(many=True)
role_schema = RoleSchema()
role_schema_with_users = RoleSchemaWithUsers()
