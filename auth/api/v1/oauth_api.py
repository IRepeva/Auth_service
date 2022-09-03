from http import HTTPStatus
from urllib.parse import urlencode

import requests
from flask import request, Blueprint, redirect

from api.models import User, SocialAccount
from api.v1.user_api import (
    registry, login_user, add_new_user
)
from api.v1.utils.other import generate_random_string
from core.oauth_params import OAUTH_DATA
from core.settings import oauth_settings
from databases import db

oauth_blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')

OAUTH_PREFIX = '/oauth'
tag = 'oauth'


def make_authorize_url(service):
    base_auth_url = OAUTH_DATA[service]['authorization_endpoint']
    params = f'?response_type=code&client_id={oauth_settings.CLIENT_ID}'
    return base_auth_url + params


def make_authorize_body(code):
    return urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': oauth_settings.CLIENT_ID,
        'client_secret': oauth_settings.CLIENT_SECRET
    })


def get_userinfo_url(service):
    base_userinfo_url = OAUTH_DATA[service]['userinfo_endpoint']
    params = f'?format=json&with_openid_identity=1'
    return base_userinfo_url + params


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
    social_service_name = 'yandex'

    if code := request.args.get('code', False):
        data = make_authorize_body(code)
        token_url = OAUTH_DATA[social_service_name]['token_endpoint']
        token_response = requests.post(token_url, data=data).json()

        user_info_request = get_userinfo_url(social_service_name)
        headers = {'Authorization': f'OAuth {token_response["access_token"]}'}

        user_info = requests.post(user_info_request, headers=headers).json()
        user = User.get_user_by_social_account(
            user_info.get('id'), social_service_name
        )
        if user:
            response = login_user(user, request.headers['User-Agent'])
            return response, HTTPStatus.OK

        user_email = user_info['default_email'].lower()
        user = db.session.query(User).filter(User.email == user_email).first()
        if not user:
            password = generate_random_string()
            user = add_new_user(user_email, password)

        add_social_account(user.id, user_info['id'], social_service_name)
        response = login_user(user, request.headers['User-Agent'])
        return response, HTTPStatus.OK

    authorize_url = make_authorize_url(social_service_name)
    return redirect(authorize_url)
