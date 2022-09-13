from api.v1.utils.other import generate_random_number_string
from captcha.image import ImageCaptcha

CAPTCHA_KEY = 'captcha'


def create_captcha(width=250, height=125):
    random_number = generate_random_number_string()
    image_captcha = ImageCaptcha(width=width, height=height)
    image_generated = image_captcha.generate(random_number)
    image_captcha.write(random_number, './static/captcha.png')
    return random_number
