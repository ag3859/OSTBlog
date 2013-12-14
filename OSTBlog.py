import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users 
from google.appengine.ext.webapp import template

class Blog(ndb.Model):
    name = ndb.StringProperty()
    user = ndb.UserProperty()
    
class Post(ndb.Model):
    title = ndb.StringProperty()
    blogId = ndb.IntegerProperty()
    body = ndb.TextProperty()
    user = ndb.UserProperty()
    createDate = ndb.DateTimeProperty(auto_now_add=True)
    modifyDate = ndb.DateTimeProperty(auto_now=True)
    cappedText = ndb.StringProperty()
    
class HomePage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            logInOutUrl = users.create_logout_url(self.request.uri)
            logInOutUrlText = "Logout"
        else:
            logInOutUrl = users.create_login_url(self.request.uri)
            logInOutUrlText = "Login"
            
        query = Blog.query()
        listOfBlogs = query.fetch()
        
        templates = {
                    'listOfBlogs':listOfBlogs,
                    'logInOutUrl':logInOutUrl,
                    'logInOutUrlText':logInOutUrlText,
                    }    
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
            'templates/blogListing.html'),
        templates))
        

app = webapp2.WSGIApplication([
       ('/', HomePage),                        
], debug=True)
        
        
        
        
        
        
        
        
        