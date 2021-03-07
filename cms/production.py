import os
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from cms.settings import *

DEBUG = False

# Sentry configuration
# https://sentry.megsupporttools.com/meg/mat-cms/
sentry_sdk.init(
    dsn='', release='1.3.0',
    integrations=[CeleryIntegration(), DjangoIntegration()],
    # associates users to errors
    send_default_pii=True
)

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', True)
# If True, browsers may ensure that the cookie is only sent under an HTTPS connection
SESSION_COOKIE_SECURE = os.environ.get('SECURE_SSL_REDIRECT', True)
# This will ensure that the CSRF Token is only sent over HTTPS
CSRF_COOKIE_SECURE = os.environ.get('SECURE_SSL_REDIRECT', True)
