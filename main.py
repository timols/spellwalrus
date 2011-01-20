#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from calling import views as calling_views
from users import views as registration_views


def main():
    routes = [
    
        ('/',                   registration_views.RegistrationHandler),
        ('/success',    registration_views.RegistrationSuccessHandler),
        
        (r'/(\d+)',             registration_views.ResultsHandler),
                                    
        ('/twilio/question',            calling_views.QuestionRenderer),
        ('/twilio/question/callback',   calling_views.QuestionResponder),
        
        ('/twilio/validation',          calling_views.ValidationRenderer),
        ('/twilio/validation/callback', calling_views.ValidationResponder),
        
        ('/jobs/make-wakeup-calls', calling_views.ScheduledCallMaker),
    ]

    application = webapp.WSGIApplication(routes, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
