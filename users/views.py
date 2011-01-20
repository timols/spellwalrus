import cgi
import datetime
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from calling.models import Call

from users.models import User
from settings import WALRUS_DOMAIN


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')


class RegistrationHandler(webapp.RequestHandler):
    def get(self):
        """
        Allow a user to submit their registration details such as phone
        number and wakeup time
        """
        path = os.path.join(TEMPLATE_DIR, 'registration.html')
        self.response.out.write(template.render(path, {}))
        
    def post(self):
        """
        Register a user for wakeup calls
        """
        params = ('phone_number', 'wakeup_time', 'include_weekends')
        phone_number, wakeup_time, include_weekends = [
            cgi.escape(self.request.get(key)) for key in params
        ]

        def parse_time(s):
            return {'730': datetime.time(7, 30),
                    '800': datetime.time(8, 00)}[s]
        
        # Create a user for the given details. Validation of phone numbers
        # will occur through twilio, at which point we'll set the user's
        # `validated` attribute to true
        user = User(**{
            'phone_number': phone_number, 
            'wakeup_time': parse_time(wakeup_time),
            'include_weekends': bool(include_weekends)
        })

        user.put()
        validation_call_url = "%s/twilio/validation?user_key=%s" % \
                              (WALRUS_DOMAIN, user.key())
        user.call(validation_call_url)
        self.redirect("/success?user_id=%s" % user.key().id())
        
        
class RegistrationSuccessHandler(webapp.RequestHandler):
    def get(self):
        user_id = cgi.escape(self.request.get('user_id'))
        template_values = {'domain': WALRUS_DOMAIN, 'user_id': user_id}
        path = os.path.join(TEMPLATE_DIR, 'registration_success.html')
        self.response.out.write(template.render(path, template_values))


class ResultsHandler(webapp.RequestHandler):
    def get(self, user_id):
        user = User.get_by_id(int(user_id))
        all_calls = Call.all().filter('user =', user)
        correct_calls = Call.all().filter('user =', user) \
                        .filter('correct_response =', True)
        template_values = {'user': user, "calls": all_calls,
                           'correct_calls': correct_calls
        }
        path = os.path.join(TEMPLATE_DIR, 'results.html')
        self.response.out.write(template.render(path, template_values))