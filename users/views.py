import calendar
import cgi
import datetime
import os
import urllib

from google.appengine.ext.webapp import template
from django.utils import simplejson

from calling.models import Call
from framework.handlers import BaseHandler
from users.models import User
from settings import WALRUS_DOMAIN, TEMPLATE_DIR


class RegistrationHandler(BaseHandler):
    def get(self):
        """
        Allow a user to submit their registration details such as phone
        number and wakeup time
        """
        self.__render()
        
    def post(self):
        """
        Register a user for wakeup calls
        """
        params = {'phone_number': None, 'timezone': None 
                  'wakeup_hour': None, 'wakeup_minute': None}
                  
        for k, v in params.items():
            params[k] = cgi.escape(self.request.get(k))
            
        params['wakeup_hour_options'] = [6, 7, 8, 9]
        params['wakeup_minute_options'] = ['00', '15', '30', '45']
        
        if not params['phone_number']:
            params['error'] = 'you forgot to give us your number'
            return self.__render(params)

        # Create a user for the given details. Validation of phone numbers
        # will occur through twilio, at which point we'll set the user's
        # `validated` attribute to true
        wakeup_time = datetime.time(int(params['wakeup_hour'])
                                    int(params['wakeup_minute']))
        user = User(**{'phone_number': params['phone_number'],
                       'wakeup_time': wakeup_time,
                       'timezone': params['timezone']})

        user.put()
        validation_call_url = "%s/twilio/validation?user_key=%s" % \
                              (WALRUS_DOMAIN, user.key())
        twilio_res = user.call(validation_call_url)
        if twilio_res:
            self.redirect("/confirm?user_id=%s" % user.key().id())
        else:
            params['error'] = 'that number is invalid'
            
    def __render(self, context={}):
        path = os.path.join(TEMPLATE_DIR, 'registration.html')
        self.response.out.write(template.render(path, context))
        
        
class ConfirmationHandler(BaseHandler):
    def get(self):
        """
        The page telling the user to check her phone for confirmation
        """
        user_id = cgi.escape(self.request.get('user_id'))
        user = User.get_by_id(int(user_id))
        template_values = {'domain': WALRUS_DOMAIN, 'user': user}
        path = os.path.join(TEMPLATE_DIR, 'registration_confirm.html')
        self.response.out.write(template.render(path, template_values))
        
        
class StatusHandler(BaseHandler):
    def get(self, user_id):
        """
        Check the status of the user's confirmation, returning JSON
        """
        user = User.get_by_id(int(user_id))
        if user.validated:
            res = simplejson.dumps({'status': 'success'})
            return self.response.out.write(res)
            
        return self.response.out.write(simplejson.dumps({'status': 'noupdate'}))
        

class SuccessHandler(BaseHandler):
    def get(self):
        """
        User succeed
        """
        user_id = cgi.escape(self.request.get('user_id'))
        user = User.get_by_id(int(user_id))
        template_values = {'domain': WALRUS_DOMAIN, 'user': user}
        path = os.path.join(TEMPLATE_DIR, 'registration_success.html')
        self.response.out.write(template.render(path, template_values))


class ResultsHandler(BaseHandler):
    def get(self, phone_number):
        """
        Show a calendar summary of the user's responses to wakeup calls
        
        !! This will explode in 2012
        """
        user = User.all().filter('phone_number =', "+%s" % phone_number).get()
        if user is None:
            return self.http404()
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
    
