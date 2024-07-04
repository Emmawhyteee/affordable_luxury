# SECRET_KEY='justluxury'
# FLASK_ENV='development'
# DEBUG=True
# ADMIN_EMAIL='emmatexiii@gmail.com'


class Config(object):
   MERCHANT_KEY='my secret key'


class TestConfig(Config):
   MERCHANT_KEY='test environment'