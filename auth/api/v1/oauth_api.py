from http import HTTPStatus

from api.models import SocialAccount
from api.v1.user_api import registry, login_user
from databases import db
from flask import request, Blueprint, redirect, jsonify

oauth_blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')

OAUTH_PREFIX = '/oauth'
tag = 'oauth'


def add_social_account(user_id, social_id, social_service):
    social_account = SocialAccount(
        user_id=user_id,
        social_user_id=social_id,
        social_service=social_service
    )
    db.session.add(social_account)
    db.session.commit()


@registry.handles(
    rule=f'{OAUTH_PREFIX}/<provider>',
    method='GET',
    tags=[tag]
)
def oauth_authorize(provider):
    """User login via OAuth provider"""
    from core.oauth import BaseOauthProvider
    oauth_provider = BaseOauthProvider.get_provider(provider)

    if code := request.args.get('code'):
        oauth_data = oauth_provider.get_oauth_data(code)

        user_social_id, user_email = oauth_provider.get_user_data(oauth_data)
        if user_social_id is None:
            return (
                jsonify({"msg": "Authentication failed"}),
                HTTPStatus.UNAUTHORIZED
            )

        user = oauth_provider.get_user(user_social_id, user_email)

        app_tokens = login_user(user, request.headers['User-Agent'])
        return app_tokens, HTTPStatus.OK

    authorize_url = oauth_provider.make_authorize_url()
    return redirect(authorize_url)
