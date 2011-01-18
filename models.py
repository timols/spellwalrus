import datetime

from google.appengine.ext import db


class User(db.Model):
    """
    A user of the service
    """
    phone_number        = db.PhoneNumberProperty(required=True)
    wakeup_time         = db.TimeProperty(required=True)
    include_weekends    = db.BooleanProperty(default=False)
    validated           = db.BooleanProperty(default=False)
    created             = db.DateTimeProperty(auto_now_add=True)
    edited              = db.DateTimeProperty(auto_now=True)
    
    def recently_called(self):
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        calls = Call.all()
        calls.filter('user =', self)
        calls.filter('created >', an_hour_ago)
        return calls.count() != 0

    def unique(self):
        users = User.all()
        users.filter('phone_number =', self.phone_number)
        return users.count() == 0

   
class Call(db.Model):
    """
    A response by a user to an automated wake up call
    """
    user                = db.ReferenceProperty(User)
    correct_response    = db.BooleanProperty()
    created             = db.DateTimeProperty(auto_now_add=True)