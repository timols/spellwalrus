#!/usr/bin/env python

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
    'To' : '(646) 823-0958',
    'Url' : 'http://3f36.localtunnel.com/calls/ask',
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

