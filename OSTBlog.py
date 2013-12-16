import os
import webapp2
from google.appengine.ext import ndb, db
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
    blogName = ndb.StringProperty()
    body = ndb.TextProperty()
    user = ndb.UserProperty()
    createDate = ndb.DateTimeProperty(auto_now_add=True)
    modifyDate = ndb.DateTimeProperty(auto_now=True)
    cappedText = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    image = ndb.BlobProperty()
    
       
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
        
        query = Post.query()
        tags = []
        for blog in query:
            tags.extend(blog.tags)
                
        #tagsStripped = [str(item).strip() for item in tags]
        #listOfTags = list(set(tagsStripped))
        listOfTags = list(set(tags))
                
        templates = {
                    'listOfBlogs':listOfBlogs,
                    'logInOutUrl':logInOutUrl,
                    'logInOutUrlText':logInOutUrlText,
                    'listOfTags':listOfTags
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
        self.redirect(str('/'+blog.name+'/'+str(blogId)+'/viewBlogPostings.html'));

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
          'templates/viewBlogPostings.html'),
        templates))



class CreatePost(webapp2.RequestHandler):
    def get(self):
        url=os.environ['PATH_INFO']
        blogName=url.split('/')[1]        
        blogId=url.split('/')[2]
        
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
          'templates/newPost.html'),
        templates))
        
    def post(self):
        url=os.environ['PATH_INFO']
        blogName=url.split('/')[1]        
        blogId=url.split('/')[2]        
        post = Post();
        post.blogId = int(blogId)
        post.blogName = blogName
        post.user = users.get_current_user()
        post.title = self.request.get('title')        
        post.body = self.request.get('body')
        post.cappedText = post.body[0:500]
        post.tags = self.request.get('tags').split(",")
        post.put()
        time.sleep(0.5)
        query = Post.query().filter(Post.title==post.title).filter(Post.user==post.user).order(-Post.createDate).fetch();
        postId = query[0].key.id()
        print postId
        self.redirect(str('/' + blogName + '/' + str(blogId) + '/'+post.title+'/'+str(postId)+'/viewPost.html'));



class ViewPost(webapp2.RequestHandler):
    def get(self):
        url=os.environ['PATH_INFO']
        blogName=url.split('/')[1]        
        blogId=url.split('/')[2]
        postTitle=url.split('/')[3]
        postId=url.split('/')[4]
        post = Post.get_by_id(int(postId))        
        if users.get_current_user():
            logInOutUrl = users.create_logout_url(self.request.uri)
            logInOutUrlText = 'Logout'
        
        else:            
            logInOutUrl = users.create_login_url(self.request.uri)
            logInOutUrlText = 'Login'
            
        templates = {
            'post': post,              
            'logInOutUrl': logInOutUrl,               
            'logInOutUrlText': logInOutUrlText,
            'userId':users.get_current_user(),
            'blogname':blogName,
            'blogId':blogId
        }
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
          'templates/viewPost.html'),
        templates))


class EditPost(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            logInOutUrl = users.create_logout_url(self.request.uri)
            logInOutUrlText = 'Logout'
        
        else:          
            self.redirect(users.create_login_url())  
            logInOutUrl = users.create_login_url(self.request.uri)
            logInOutUrlText = 'Login'
            
        url=os.environ['PATH_INFO']
        blogName=url.split('/')[1]        
        blogId=url.split('/')[2]
        postTitle=url.split('/')[3]
        postId=url.split('/')[4]
        post = Post.query().filter(Post.title==postTitle).filter(Post.blogId == int(blogId)).fetch()
                
        print(post)
            
        templates = {
            'post': post[0],              
            'logInOutUrl': logInOutUrl,               
            'logInOutUrlText': logInOutUrlText,
            'userId':users.get_current_user(),
            'blogname':blogName,
            'blogId':blogId
        }
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
          'templates/editPost.html'),
        templates))
        
    def post(self):
        url = os.environ['PATH_INFO']
        blogName = url.split('/')[1]        
        blogId = url.split('/')[2]        
        postTitle = url.split('/')[3]
        postId = url.split('/')[4]
            
        post = Post.get_by_id(int(postId));
        post.title = self.request.get('title')        
        post.body = self.request.get('body')
        post.cappedText = post.body[0:500]
        tags = self.request.get('tags').split(",")
        post.tags = [item.strip() for item in tags]
#        post.modifyDate = 
        post.put()
        time.sleep(0.5)
        query = Post.query().filter(Post.title == post.title).filter(Post.blogId == int(blogId)).order(-Post.createDate).fetch();
        print str('/' + blogName + '/' + str(blogId) + '/' + post.title + '/' + str(postId) + '/viewPost.html')
        self.redirect(str('/' + blogName + '/' + str(blogId) + '/' + post.title + '/' + str(postId) + '/viewPost.html'))


class ViewTagPostings(webapp2.RequestHandler):
    def get(self):
        url=os.environ['PATH_INFO']
        tag=url.split('/')[3]
                
        query = Post.query().fetch()
        
        relevantQueries = [item for item in query if (tag in item.tags)]
        
        paginator=Paginator(relevantQueries, 10)
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
            'tag':tag,
            'posts': pageWithPosts,              
            'logInOutUrl': logInOutUrl,               
            'logInOutUrlText': logInOutUrlText,
            'userId':users.get_current_user()
        }
        
        self.response.write(template.render(
        os.path.join(os.path.dirname(__file__),
          'templates/viewTagPostings.html'),
        templates))


app = webapp2.WSGIApplication([
       ('/', HomePage),
       ('/newBlogPage.html', CreateBlog),  
       (r'.*/viewBlogPostings.html$', ViewBlog),
       (r'.*/newPost.html$', CreatePost),
       (r'.*/viewPost.html$', ViewPost),
       (r'.*/editPost.html$', EditPost),
       (r'.*/viewTagPostings.html$', ViewTagPostings),
], debug=True)
