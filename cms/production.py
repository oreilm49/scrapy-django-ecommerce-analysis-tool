from cms.settings import *

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', True)
# If True, browsers may ensure that the cookie is only sent under an HTTPS connection
SESSION_COOKIE_SECURE = os.environ.get('SECURE_SSL_REDIRECT', True)
# This will ensure that the CSRF Token is only sent over HTTPS
CSRF_COOKIE_SECURE = os.environ.get('SECURE_SSL_REDIRECT', True)
