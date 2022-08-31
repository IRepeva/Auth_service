from marshmallow import fields, validates_schema, ValidationError
from marshmallow.validate import Email, Length

from api.models import User, LoginHistory
from extensions import ma


class LoginHistorySchema(ma.SQLAlchemyAutoSchema):
    date = fields.String()

    class Meta:
        model = LoginHistory
        exclude = ('id',)


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(validate=Email(), required=True)
    password = fields.Str(
        required=True,
        validate=Length(min=6, max=36),
        load_only=True
    )
    date_created = fields.String()

    class Meta:
        model = User
        exclude = ('id',)


class UserLoginSchema(UserSchema):
    password_conf = fields.Str(
        validate=Length(min=6, max=36),
        load_only=True
    )

    @validates_schema
    def validate_password(self, data, **kwargs):
        if (
                data.get('password_conf')
                and data['password'] != data['password_conf']
        ):
            raise ValidationError('Passwords should be equal! Please try again')


class UserProfileSchema(UserSchema):
    class Meta:
        model = User
        exclude = ('id', 'password')


user_login_schema = UserLoginSchema()
user_profile_schema = UserProfileSchema()

login_history_schema = LoginHistorySchema(many=True)
