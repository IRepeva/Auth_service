from http import HTTPStatus

from flask import request, Blueprint, redirect

from api.models import SocialAccount
from api.v1.user_api import registry, login_user
from core.oauth import YandexOAuth, VKOAuth
from databases import db

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
    rule=f'{OAUTH_PREFIX}/yandex',
    method='GET',
    tags=[tag]
)
def yandex():
    """User login via Yandex"""
    yandex_oauth = YandexOAuth()

    if code := request.args.get('code'):
        tokens = yandex_oauth.get_oauth_data(code)

        user_info = yandex_oauth.get_user_info(tokens)
        user_social_id, user_email = (
            user_info.get('id'), user_info['default_email']
        )
        user = yandex_oauth.get_user(user_social_id, user_email.lower())

        app_tokens = login_user(user, request.headers['User-Agent'])
        return app_tokens, HTTPStatus.OK

    authorize_url = yandex_oauth.make_authorize_url()
    return redirect(authorize_url)


@registry.handles(
    rule=f'{OAUTH_PREFIX}/vk',
    method='GET',
    tags=[tag]
)
def vk():
    """User login via VK"""
    vk_oauth = VKOAuth()
    redirect_uri = vk_oauth.service_data['redirect_uri']

    if code := request.args.get('code'):
        user_info = vk_oauth.get_oauth_data(code, redirect_uri=redirect_uri)

        user_social_id, user_email = (
            user_info.get('user_id'), user_info.get('email')
        )
        user = vk_oauth.get_user(user_social_id, user_email.lower())

        app_tokens = login_user(user, request.headers['User-Agent'])
        return app_tokens, HTTPStatus.OK

    authorize_url = vk_oauth.make_authorize_url(
        redirect_uri=redirect_uri,
        scope='email'
    )
    return redirect(authorize_url)
