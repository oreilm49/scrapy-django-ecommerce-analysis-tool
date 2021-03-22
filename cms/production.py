import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from cms.settings import *

DEBUG = False
SECRET_KEY = "Eg8BktP1A5pDEsPPeJ7jhIg19SS4vUpR"

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', True)
# If True, browsers may ensure that the cookie is only sent under an HTTPS connection
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', True)
# This will ensure that the CSRF Token is only sent over HTTPS
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', True)

SENDGRID_SANDBOX_MODE_IN_DEBUG = False

sentry_sdk.init(
    dsn='https://d7219358ffd142488ed74e36e642608e@o556601.ingest.sentry.io/5687819',
    integrations=[CeleryIntegration(), DjangoIntegration()],
    # associates users to errors
    send_default_pii=True
)
