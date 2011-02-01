# Project-wide settings for this-is-a-walrus
import os

WALRUS_DOMAIN = "http://www.spellwalrus.com"
TWILIO_API_VERSION = '2010-04-01'

# Twilio AccountSid and AuthToken
TWILIO_ACCOUNT_SID = 'ACaf6b71b908e26093ee7fc9d2562e89d9'
TWILIO_ACCOUNT_TOKEN = 'e9c6bedc9f1f029d4ff9ec8661e7a9e6'

# Outgoing Caller ID previously validated with Twilio
TWILIO_CALLER_ID = '(646) 450-2065';

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


try:
    from local_settings.py import *
except ImportError:
    pass
