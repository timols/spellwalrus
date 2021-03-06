import cgi
import datetime
import os

from framework.handlers import BaseHandler
from libs import twilio
from settings import WALRUS_DOMAIN
from users.models import User

from call_responses import WAKEUP_CALL, VALIDATION_CALL, \
    YOU_SPELLED_THE_WALRUS, THATS_NOT_HOW_YOU_SPELL_WALRUS, \
    NUMBER_WAS_VALIDATED, NUMBER_WAS_NOT_VALIDATED, UNSUBSCRIBE
from keywords import TODAYS_KEYWORD
from models import Call
from utils import chars_to_digits


# TwiML Renderers - return TwiML to define a phone call when hit by twilio

class QuestionRenderer(BaseHandler):
    def post(self):
        """
        Tell twilio what question to say during the automated wakeup call,
        for instance "Please spell WALRUS".
        """
        res = WAKEUP_CALL % {'domain': WALRUS_DOMAIN, 
                             'keyword': TODAYS_KEYWORD['word'],
                             'sentence': TODAYS_KEYWORD['sentence']}
        return self.return_XML(res)


class ValidationRenderer(BaseHandler):
    def post(self):
        """
        Validate the users phone number by a phone prompt before adding
        to the datastore
        """
        key = cgi.escape(self.request.get('user_key'))
        res = VALIDATION_CALL % {'domain': WALRUS_DOMAIN, 'user_key': key}
        return self.return_XML(res)
    
        
# TwiML Responders - callbacks hit by twilio during a phone call, as a 
# consequence of user actions such as entering digits
        
class QuestionResponder(BaseHandler):
    def get(self):
        """
        Determine whether the user correctly spelled the key word during
        her wakeup call.
        
        For instance, 'W-A-L-R-U-S' is correct.
        """
        digits = self.request.get('Digits')
        the_number = self.request.get('To')

        try:
            the_user = User.all().filter('phone_number =', the_number).fetch(1)[0]
        except IndexError:
            return 'FAIL'
        
        stop = (digits == chars_to_digits('stop'))
        correct = (digits == chars_to_digits(TODAYS_KEYWORD['word']))
        
        call_record = Call(user=the_user, correct_response=correct)
        call_record.put()
        
        if correct:
            res = YOU_SPELLED_THE_WALRUS
        else:
            if stop:
                the_user.delete()
                res = UNSUBSCRIBE
            else:
                res = THATS_NOT_HOW_YOU_SPELL_WALRUS % {
                    'keyword': TODAYS_KEYWORD['word'],
                    'domain': WALRUS_DOMAIN
                }
        return self.return_XML(res)


class ValidationResponder(BaseHandler):
    def post(self):
        """
        Determine whether the user correctly validated her phone number.
        """
        params = ('Digits', 'To', 'user_key')
        digits, to, user_key = [self.request.get(p) for p in params]
        
        if digits != '1':
            res = NUMBER_WAS_NOT_VALIDATED % \
                  {'user_key': user_key, 'domain': WALRUS_DOMAIN}
            return self.return_XML(res)
        
        # Validation is complete, so save/update user details
        user = User.find_or_validate(to, user_key)

        return self.return_XML(NUMBER_WAS_VALIDATED)

        
# Scheduled jobs

class ScheduledCallMaker(BaseHandler):
    def get(self):
        """
        Check if any calls are scheduled to be made this minute, 
        and if so, tell twilio to make them
        """
        now = datetime.datetime.now()
        
        now_time = now.time()
        lookback_time = (now - datetime.timedelta(minutes=5)).time()
        all_users = User.all().filter('wakeup_time <', now_time).filter('wakeup_time >', lookback_time)
        
        # exclude users for which their timezone puts them in a weekend
        all_users = filter(lambda u: not u.is_local_weekend(), all_users)
        
        # exclude users for which a call has recently been made
        all_users = filter(lambda u: not u.recently_called(), all_users)

        # for each number, tell twilio to make a call
        question_url = "%s/twilio/question" % WALRUS_DOMAIN
        [u.call(question_url) for u in all_users]
        
        self.response.out.write(str(now_time))

        