import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users 
from google.appengine.ext.webapp import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time

class Blog(ndb.Model):
    name = ndb.StringProperty()
    user = ndb.UserProperty()
    createDate = ndb.DateTimeProperty(auto_now_add=True)

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
        
        
class CreateBlog(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            logInOutUrl = users.create_logout_url(self.request.uri)
            logInOutUrlText = "Logout"
        else:
            self.redirect(users.create_login_url())
            logInOutUrl = users.create_login_url(self.request.uri)
            logInOutUrlText = "Login"
        
        templates = {
            'logInOutUrl':logInOutUrl,
            'logInOutUrlText':logInOutUrlText,
        }
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
          'templates/newBlog.html'),
        templates))
        
    def post(self):
        blog = Blog();
        blog.user = users.get_current_user()
        blog.name = self.request.get('name')
        blog.put()
        time.sleep(0.5)
        query = Blog.query().filter(Blog.name==blog.name).filter(Blog.user==blog.user).order(-Blog.createDate).fetch();
        blogId = query[0].key.id()
        print blogId
        self.redirect(str('/'+blog.name+'/'+str(blogId)+'/viewBlogPostings'));

class ViewBlog(webapp2.RequestHandler):
    def get(self):
        url=os.environ['PATH_INFO']
        blogName=url.split('/')[1]
        blogId=url.split('/')[2]
        query = Post.query().filter(Post.blogId==int(blogId)).order(-Post.createDate)
        posts = query.fetch()
        paginator=Paginator(posts, 10)
        newPage = self.request.get('page')
        try:
            pageWithPosts = paginator.page(newPage)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            pageWithPosts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            pageWithPosts = paginator.page(paginator.num_pages)
        
        if users.get_current_user():
            logInOutUrl = users.create_logout_url(self.request.uri)
            logInOutUrlText = 'Logout'
        
        else:            
            logInOutUrl = users.create_login_url(self.request.uri)
            logInOutUrlText = 'Login'
            
        templates = {
            'posts': pageWithPosts,              
            'logInOutUrl': logInOutUrl,               
            'logInOutUrlText': logInOutUrlText,
            'blogname':blogName,
            'blogId':blogId,
            'userId':users.get_current_user()
        }
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
          'templates/main.html'),
        templates))

app = webapp2.WSGIApplication([
       ('/', HomePage),
       ('/newBlogPage.html', CreateBlog),  
       (r'.*/viewBlogPostings$', ViewBlog),         
], debug=True)
        
        
        
        
        
        
        
        
        