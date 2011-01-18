#!/usr/bin/env python

import cgi
import datetime
import logging
import string
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

import twilio

from creds import TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN, TWILIO_CALLER_ID
from models import User, Call


TWILIO_API_VERSION = '2010-04-01'

WALRUS_DOMAIN

KEY_WORD = {
    'Monday': 'walrus',
    'Tuesday': 'wombat',
    'Wednesday': 'donkey',
    'Thursday': 'gazelle',
    'Friday': 'snake',
    'Saturday': 'tiger',
    'Sunday': 'swan'
}[datetime.datetime.now().strftime("%A")]


WAKEUP_CALL = """<Response>
    <Gather action="http://4axx.localtunnel.com/calls/check" method="GET" timeout="10">
        <Say>Spell the word %s.</Say>
    </Gather>
</Response>""" % KEY_WORD

YOU_SPELLED_THE_WALRUS = """<Response>
    <Say>You are correct</Say>
</Response>
"""

VALIDATION_CALL = """<Response>
    <Gather action="%(domain)s/calls/savenumber?user_key=%(user_key)s" method="POST" timeout="10">
        <Say>Please confirm your phone number by pressing 1, followed by the pound sign</Say>
    </Gather>
</Response>"""

THATS_NOT_HOW_YOU_SPELL_WALRUS = """<Response>
    <Say>That is incorrect. You give us money now</Say>
</Response>
"""


class MainHandler(webapp.RequestHandler):
    def get(self):
        """
        Allow a user to submit details
        """
        context = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, context))
        
    def post(self):
        """
        Register a user for wakeup calls
        """
        phone_number = cgi.escape(self.request.get('phone_number'))
        wakeup_time = {
            '730': datetime.time(7, 30),
            '800': datetime.time(8, 00)
        }[cgi.escape(self.request.get('wakeup_time'))]
        include_weekends = bool(cgi.escape(self.request.get('include_weekends')))
        
        user = User(phone_number=phone_number, wakeup_time=wakeup_time,
                include_weekends=include_weekends)
        if user.unique():
            user.put()
            user_key = user.key().__str__()
            initiate_call(user, "validate?user_key=" +  user_key)
            self.response.out.write("Your phone number: %s, will be receiving a phone call shortly to confirm. Please follow the prompts." % phone_number)
        else:
            self.response.out.write("A call is in progress or has already been placed to this number.")

        
class Dialer(webapp.RequestHandler):
    def get(self):
        """
        Check if any calls are scheduled to be made this minute, 
        and if so, tell twilio to make them
        """
        # for each scheduled call, get the number
        now = datetime.datetime.now()
        now_time = datetime.time(now.hour, now.minute)
        users = User.all().filter('wakeup_time =', now_time)
        
        # exclude users for which a call has recently been made
        users = filter(lambda u: not u.recently_called, users)

        # for each number, tell twilio to make a call
        for user in users:
            initiate_call(user, "ask")
                
        return 'OK'

class QuestionAsker(webapp.RequestHandler):
    def post(self):
        """
        Tell twilio what to say during the automated wakeup call
        """
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.out.write(WAKEUP_CALL)
        
        
class AnswerChecker(webapp.RequestHandler):
    def get(self):
        """
        Handle the response of the user during their automated wakeup call
        """
        digits = self.request.get('Digits')
        the_number = self.request.get('To')

        try:
            the_user = User.all().filter('phone_number =', the_number).fetch(1)[0]
        except IndexError:
            return 'FAIL'
        
        correct = digits == digitize(KEY_WORD)
        
        call_record = Call(user=the_user, correct_response=correct)
        call_record.put()
        
        
        if correct:
            response = YOU_SPELLED_THE_WALRUS
        else:
            response = THATS_NOT_HOW_YOU_SPELL_WALRUS

            
        self.response.out.write(response)

class NumberValidator(webapp.RequestHandler):
    def post(self):
        """
        Validate the users phone number by a phone prompt before adding to the datastore
        """

        key = self.request.get('user_key')

        self.response.headers['Content-Type'] = 'application/xml'
        self.response.out.write(VALIDATION_CALL % {'domain': WALRUS_DOMAIN, 'user_key': key})

class Adder(webapp.RequestHandler):
    def post(self):
        """
        Check if the user confirmed
        """
        digits = self.request.get('Digits')
        key = self.request.get('user_key')
        logging.info(key)
        
        if digits == '1':
            the_number = self.request.get('To')
            user = User.get(key)
            user.phone_number = the_number
            user.validated = True
            # if user.unique_check():
                # user.put()
            # User.get_or_insert('phone_number', the_number)
            response = YOU_SPELLED_THE_WALRUS
        else:
            logging.info('The user pressed: %s' % digits)
            response = THATS_NOT_HOW_YOU_SPELL_WALRUS
            
        self.response.out.write(response)
            

def digitize(word):
    "Given a string of characters, return the corresponding keypad digits"
    KEYPAD_MAPPING = dict(zip(string.ascii_lowercase, 
                              "22233344455566677778889999"))
    return ''.join(str(KEYPAD_MAPPING[l]) for l in word.lower())

def initiate_call(user, action):
    """
    Make a phone call to a user object given a valid action (string)
    """
    account = twilio.Account(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN)

    d = {
        'From' : TWILIO_CALLER_ID,
        'To' : user.phone_number,
        'Url' : ('http://4axx.localtunnel.com/calls/' + str(action)),
        }
    try:
        print account.request('/%s/Accounts/%s/Calls.json' % \
                             (TWILIO_API_VERSION, TWILIO_ACCOUNT_SID), 'POST', d)
    except Exception, e:
        logging.error(e)


def main():
    routes = [
        ('/', MainHandler),
        ('/calls/dial', Dialer),
        ('/calls/ask', QuestionAsker),
        ('/calls/check', AnswerChecker),
        ('/calls/validate', NumberValidator),
        ('/calls/savenumber', Adder)
    ]

    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
