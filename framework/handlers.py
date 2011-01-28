import os

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from settings import TEMPLATE_DIR


class BaseHandler(webapp.RequestHandler):
    """
    Wrapper for webapp's request handler providing handy shortcuts.
    
    You should generally subclass this for all handlers in the app,
    for the sake of consistency.
    """
    def http404(self):
        """
        Render our custom 404 template, with the correct status 
        """
        self.error(404)
        path = os.path.join(TEMPLATE_DIR, '404.html')
        self.response.out.write(template.render(path, {}))
    
    def return_XML(self, res):
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.out.write(res)
        
    def return_JSON(self, res):
        self.response.headers['Content-Type'] = 'application/json'        
        self.response.out.write(res)        
        
    def write_JSON(self, obj):
        self.return_JSON(simplejson.dumps(obj))
        
        
class NotFoundHandler(BaseHandler):
    def get(self):
        return self.http404()
        
    post = head = options = put = delete = trace = get