from google.appengine.ext import db
from users.models import User

   
class Call(db.Model):
    """
    A response by a user to an automated wake up call
    """
    user                = db.ReferenceProperty(User)
    correct_response    = db.BooleanProperty()
    created             = db.DateTimeProperty(auto_now_add=True)