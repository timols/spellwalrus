import datetime
import logging

from google.appengine.ext import db

from libs.pytz.gae import pytz
from libs import twilio
from settings import TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN, \
    TWILIO_CALLER_ID, TWILIO_API_VERSION


class User(db.Model):
    """
    A user of the service
    """
    phone_number        = db.PhoneNumberProperty(required=True)
    wakeup_time         = db.TimeProperty(required=True)
    timezone            = db.StringProperty()
    validated           = db.BooleanProperty(default=False)
    created             = db.DateTimeProperty(auto_now_add=True)
    edited              = db.DateTimeProperty(auto_now=True)
    
    @classmethod
    def find_or_validate(cls, phone_number, key):
        """
        Find a validated user with the given phone number and update her
        wake up call settings, otherwise, validate the user with the given key
        """
        users_for_number = cls.all() \
                              .filter('phone_number =', phone_number) \
                              .filter('validated =', True)
        user_for_key = cls.get(key)
        
        try:
            user = users_for_number[0]
            # Valid user was found, so update the wake up call settings
            user.wakeup_time = user_for_key.wakeup_time
            user_for_key.delete()
        except IndexError:
            user = user_for_key
            # Update the user's phone number with the Twilio standardized
            # phone number (e.g. (646) 823-1111 -> +16468231111)
            user.phone_number = phone_number
            user.validated = True
        
        user.put()
        return user
        
    
    def recently_called(self):
        from calling.models import Call
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        calls = Call.all()
        calls.filter('user =', self)
        calls.filter('created >', an_hour_ago)
        return calls.count() != 0
        
    def call(self, render_url):
        """
        Initiate a phone call to the user through twilio.
        
        `render_url' defines our url which twilio requests to determine
        the TwiML for the automated call
        """
        account = twilio.Account(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_TOKEN)

        data = {'From' : TWILIO_CALLER_ID,
                'To' : self.phone_number,
                'Url' : render_url}
        try:
            request_url = "/%s/Accounts/%s/Calls.json" % \
                          (TWILIO_API_VERSION, TWILIO_ACCOUNT_SID)
                          
            logging.info("*" * 50)
            logging.info("Request to twilio: %s" % request_url)
            logging.info("with arguments:")
            [logging.info("%s: %s" % (k, v)) for k, v in data.items()]
            
            return account.request(request_url, 'POST', data)
        except Exception, e:
            logging.error(e)
    
    def history_url(self):
        return "/%s" % self.phone_number.replace('+', '')
        
    def is_local_weekend(self):
        utc = pytz.utc
        tz = pytz.timezone(self.timezone)
        now = datetime.datetime.now()
        local_now = utc.localize(now).astimezone(tz)
        return local_now.isoweekday() in (6, 7)