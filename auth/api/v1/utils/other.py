import string

from api.models import LoginHistory
from secrets import choice as secrets_choice


def get_device_type(user_agent):
    match user_agent:
        case user_agent.is_mobile:
            return LoginHistory.DEVICE_TYPES['mobile']
        case user_agent.is_pc:
            return LoginHistory.DEVICE_TYPES['pc']
        case user_agent.is_tablet:
            return LoginHistory.DEVICE_TYPES['tablet']
    return LoginHistory.DEVICE_TYPES['other']


def generate_random_string():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets_choice(alphabet) for _ in range(16))
