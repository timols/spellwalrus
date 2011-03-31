# Project-wide settings for this-is-a-walrus
import os

WALRUS_DOMAIN = "http://www.spellwalrus.com"
TWILIO_API_VERSION = '2010-04-01'

# Twilio AccountSid and AuthToken
TWILIO_ACCOUNT_SID = 'TWILIO_ACCOUNT_SID'
TWILIO_ACCOUNT_TOKEN = 'TWILIO_ACCOUNT_TOKEN'

# Outgoing Caller ID previously validated with Twilio
TWILIO_CALLER_ID = 'TWILIO_CALLER_ID';

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


try:
    from local_settings.py import *
except ImportError:
    pass
