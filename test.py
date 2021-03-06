#!/usr/bin/env python
from settings import WALRUS_DOMAIN
import twilio
from creds import TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN, TWILIO_CALLER_ID

# Twilio REST API version
API_VERSION = '2010-04-01'

# Create a Twilio REST account object using your Twilio account ID and token
account = twilio.Account(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN)

# ===========================================================================
# 1. Initiate a new outbound call to 415-555-1212
#    uses a HTTP POST
d = {
    'From' : TWILIO_CALLER_ID,
    'To' : '(865) 484-6657',
    'Url' : '%s/jobs/make-wakeup-calls' % WALRUS_DOMAIN,
}
try:
    print account.request('/%s/Accounts/%s/Calls.json' % \
                              (API_VERSION, TWILIO_ACCOUNT_SID), 'POST', d)
except Exception, e:
    print e
    print e.read()

# ===========================================================================
# 2. Get a list of recent completed calls (i.e. Status = 2)
#    uses a HTTP GET
d = { 'Status':2, }
try:
    print account.request('/%s/Accounts/%s/Calls.json' % \
                              (API_VERSION, TWILIO_ACCOUNT_SID), 'GET', d)
except Exception, e:
    print e
    print e.read()

