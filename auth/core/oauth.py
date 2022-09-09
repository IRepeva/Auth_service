from urllib.parse import urlencode

import requests

from api.models import User
from api.v1.user_api import add_new_user
from api.v1.utils.other import generate_fake_email
from core.settings import oauth_settings
from databases import db

OAUTH_DATA = {
    'yandex': {
        'authorization_endpoint': 'https://oauth.yandex.ru/authorize',
        'redirect_endpoint': 'http://0.0.0.0/oauth/yandex',
        'token_endpoint': 'https://oauth.yandex.ru/token',
        'userinfo_endpoint': 'https://login.yandex.ru/info'
    },
    'vk': {
        'authorization_endpoint': 'https://oauth.vk.com/authorize',
        'redirect_uri': 'http://0.0.0.0/oauth/vk',
        'token_endpoint': 'https://oauth.vk.ru/access_token'
    }
}


class BaseOauthService:
    SERVICE_NAME = None
    CLIENT_ID = None
    CLIENT_SECRET = None

    @property
    def service_data(self):
        return OAUTH_DATA[self.SERVICE_NAME]

    def make_authorize_url(self, **kwargs):
        base_auth_url = self.service_data['authorization_endpoint'] + '?'
        params = {'client_id': self.CLIENT_ID, 'response_type': 'code'}
        if kwargs:
            params.update(kwargs)

        return base_auth_url + '&'.join([f'{k}={v}' for k, v in params.items()])

    def make_token_endpoint_data(self, code, **kwargs):
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }
        if kwargs:
            params.update(kwargs)
        return urlencode(params)

    def get_oauth_data(self, code, **kwargs):
        data = self.make_token_endpoint_data(code, **kwargs)
        token_url = self.service_data['token_endpoint']
        return requests.post(token_url, data=data).json()

    def get_user(self, user_social_id, user_email=None):
        from api.v1.oauth_api import add_social_account

        user = User.get_user_by_social_account(
            user_social_id, self.SERVICE_NAME
        )
        if user:
            return user

        if not user_email:
            user_email = generate_fake_email()
        else:
            user_email = user_email.lower()
            user = db.session.query(User).filter(User.email == user_email).first()

        if not user:
            user = add_new_user(user_email)

        add_social_account(user.id, user_social_id, self.SERVICE_NAME)

        return user


class YandexOAuth(BaseOauthService):
    SERVICE_NAME = 'yandex'
    CLIENT_ID = oauth_settings.YANDEX_CLIENT_ID
    CLIENT_SECRET = oauth_settings.YANDEX_CLIENT_SECRET

    def get_userinfo_url(self, **kwargs):
        base_userinfo_url = self.service_data['userinfo_endpoint'] + '?'
        params = {'format': 'json', 'with_openid_identity': '1'}
        if kwargs:
            params.update(kwargs)
        return base_userinfo_url + '&'.join(
            [f'{k}={v}' for k, v in params.items()]
        )

    def get_user_info(self, tokens):
        user_info_request = self.get_userinfo_url()
        headers = {'Authorization': f'OAuth {tokens["access_token"]}'}

        return requests.post(user_info_request, headers=headers).json()


class VKOAuth(BaseOauthService):
    SERVICE_NAME = 'vk'
    CLIENT_ID = oauth_settings.VK_CLIENT_ID
    CLIENT_SECRET = oauth_settings.VK_CLIENT_SECRET
