import calendar
import cgi
import datetime
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson

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
        twilio_res = user.call(validation_call_url)
        if twilio_res:
            self.redirect("/confirm?user_id=%s" % user.key().id())
        else:
            self.redirect("/failurl")
        
        
class ConfirmationHandler(webapp.RequestHandler):
    def get(self):
        """
        The page telling the user to check her phone for confirmation
        """
        user_id = cgi.escape(self.request.get('user_id'))
        user = User.get_by_id(int(user_id))
        template_values = {'domain': WALRUS_DOMAIN, 'user': user}
        path = os.path.join(TEMPLATE_DIR, 'registration_confirm.html')
        self.response.out.write(template.render(path, template_values))
        
        
class StatusHandler(webapp.RequestHandler):
    def get(self, user_id):
        """
        Check the status of the user's confirmation, returning JSON
        """
        user = User.get_by_id(int(user_id))
        if user.validated:
            res = simplejson.dumps({'status': 'success'})
            return self.response.out.write(res)
            
        return self.response.out.write(simplejson.dumps({'status': 'noupdate'}))
        

class SuccessHandler(webapp.RequestHandler):
    def get(self):
        """
        User succeed
        """
        user_id = cgi.escape(self.request.get('user_id'))
        user = User.get_by_id(int(user_id))
        template_values = {'domain': WALRUS_DOMAIN, 'user': user}
        path = os.path.join(TEMPLATE_DIR, 'registration_success.html')
        self.response.out.write(template.render(path, template_values))


class ResultsHandler(webapp.RequestHandler):
    def get(self, user_id):
        """
        Show a calendar summary of the user's responses to wakeup calls
        
        !! This will explode in 2012
        """
        user = User.get_by_id(int(user_id))
        history = {}
        calls = Call.all().filter('user =', user)
        cal = calendar.Calendar()
        
        for call in calls:
            if not call.correct_response:
                continue
            
            call_month = call.created.strftime("%B")
            
            try:
                month_history = history[call_month]
            except KeyError:
                month_history = history[call_month] = [
                    {'day': d, 'correct_response': False} 
                    for d in cal.itermonthdays2(2011, call.created.month)
                ]
                
            for day_history in month_history:
                if day_history['day'][0] == call.created.day:
                    day_history['correct_response'] = True
                    break
                
        
        context = {'user': user, 'history': history}
        path = os.path.join(TEMPLATE_DIR, 'results.html')
        self.response.out.write(template.render(path, context))
    
