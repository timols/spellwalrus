from google.appengine.ext import db
   

class Call(db.Model):
    """
    A response by a user to an automated wake up call
    """
    from users.models import User

    user                = db.ReferenceProperty(User)
    correct_response    = db.BooleanProperty()
    created             = db.DateTimeProperty(auto_now_add=True)