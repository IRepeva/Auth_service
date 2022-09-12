from dataclasses import dataclass
from http import HTTPStatus

import core
from api.models import SocialAccount, User
from api.v1.oauth_api import OAUTH_PREFIX
from auth.conftest import BASE_EMAIL, SOCIAL_ID, db_add, BASE_ID, SOME_EMAIL
from core.oauth import BaseOauthProvider, YandexOAuth
from core.settings import oauth_settings
from databases import db

URL_OAUTH = f'{OAUTH_PREFIX}'


@dataclass
class FakeOAuth(BaseOauthProvider):
    SERVICE_NAME: str
    CLIENT_ID: str

    @classmethod
    def get_oauth_tokens(cls, code, **kwargs):
        return {'access_token': 'very_fake_token'}

    @classmethod
    def get_yandex_user_data(cls, token, **kwargs):
        return {'id': SOCIAL_ID, 'default_email': BASE_EMAIL}

    @classmethod
    def get_vk_user_data(cls, token, **kwargs):
        return {'user_id': SOCIAL_ID}


def test_yandex(client):
    url = URL_OAUTH + '/yandex'
    yandex_provider = FakeOAuth(
        'yandex',
        oauth_settings.YANDEX_CLIENT_ID
    )

    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.headers['Location'] == yandex_provider.make_authorize_url()

    core.oauth.BaseOauthProvider.get_oauth_data = FakeOAuth.get_oauth_tokens
    core.oauth.YandexOAuth.get_user_info = FakeOAuth.get_yandex_user_data

    resp = client.get(url + '?code=666')
    assert resp.status_code == HTTPStatus.OK
    assert 'access_token' in resp.data.decode()
    assert 'refresh_token' in resp.data.decode()

    social_account = db.session.query(
        SocialAccount
    ).filter(
        SocialAccount.social_user_id == SOCIAL_ID
    ).first()

    assert social_account is not None


def test_vk(client):
    url = URL_OAUTH + '/vk'
    vk_provider = FakeOAuth(
        'vk',
        oauth_settings.VK_CLIENT_ID
    )

    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.headers['Location'] == vk_provider.make_authorize_url(
        redirect_uri=vk_provider.provider_data['redirect_uri'],
        scope='email'
    )

    core.oauth.BaseOauthProvider.get_oauth_data = FakeOAuth.get_vk_user_data
    resp = client.get(url + '?code=666')
    assert resp.status_code == HTTPStatus.OK
    assert 'access_token' in resp.data.decode()
    assert 'refresh_token' in resp.data.decode()

    social_account = db.session.query(
        SocialAccount
    ).filter(
        SocialAccount.social_user_id == SOCIAL_ID
    ).first()
    assert social_account is not None


def test_get_social_user(mocker):
    base_service_inst = YandexOAuth()
    mock_add_social_acc = mocker.patch('core.oauth.add_social_account')
    present_social_data = {
                'user_id': BASE_ID,
                'social_user_id': SOCIAL_ID,
                'social_service': 'yandex'
            }
    db_add(SocialAccount(**present_social_data))

    base_service_inst.get_user(SOCIAL_ID)
    mock_add_social_acc.assert_not_called()


def test_get_db_user(mocker):
    base_service_inst = YandexOAuth()
    mock_add_social_acc = mocker.patch('core.oauth.add_social_account')

    user = db.session.query(
        User
    ).filter(
        User.email == BASE_EMAIL
    ).first()
    assert user is not None

    base_service_inst.get_user(SOCIAL_ID, BASE_EMAIL)

    mock_add_social_acc.assert_called_with(BASE_ID, SOCIAL_ID, 'yandex')


def test_new_user_no_email(mocker):
    base_service_inst = YandexOAuth()

    mock_gen_fake_email = mocker.patch('core.oauth.generate_fake_email')
    mock_gen_fake_email.return_value = 'fake.fake'
    mock_add_new_user = mocker.patch('core.oauth.add_new_user')
    mock_add_social_acc = mocker.patch('core.oauth.add_social_account')

    base_service_inst.get_user(SOCIAL_ID)

    mock_gen_fake_email.assert_called_once()
    mock_add_new_user.assert_called_with('fake.fake')
    mock_add_social_acc.assert_called_with(
        mock_add_new_user().id, SOCIAL_ID, 'yandex'
    )


def test_new_user_email(mocker):
    base_service_inst = YandexOAuth()
    mock_gen_fake_email = mocker.patch('core.oauth.generate_fake_email')
    mock_add_new_user = mocker.patch('core.oauth.add_new_user')
    mock_add_social_acc = mocker.patch('core.oauth.add_social_account')

    base_service_inst.get_user(SOCIAL_ID, SOME_EMAIL)

    mock_gen_fake_email.assert_not_called()
    mock_add_new_user.assert_called_with(SOME_EMAIL)
    mock_add_social_acc.assert_called_with(
        mock_add_new_user().id, SOCIAL_ID, 'yandex'
    )
