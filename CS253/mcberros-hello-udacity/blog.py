#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape =True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
	self.response.out.write(*a, **kw)

    def render_str(Self, template, **params):
	t=jinja_env.get_template(template)
	return t.render(params)

    def render(self, template, **kw):
	self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject=db.StringProperty(required = True)
    content=db.TextProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)
    last_modified=db.DateTimeProperty(auto_now = True)

class BlogHandler(Handler):
    def render_front(self):
	entries=db.GqlQuery("SELECT * FROM Blog ORDER BY last_modified DESC limit 10")
	self.render("front_blog.html", entries=entries)

    def get(self):
	self.render_front()

class NewPostHandler(Handler):
    def render_front(self, subject="", content="", error=""):
	content=content.replace('\n', '<br>')
        self.render("form_blog.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        subject=self.request.get("subject")
        content=self.request.get("content")

        if subject and content:
           c=Blog(subject=subject, content=content)
           c.put()
	   id_entry=c.key()
	   str_id_key=str(id_entry.id())
           self.redirect("/blog/"+str_id_key)
        else:
           error="we need both a subject and a content"
           self.render_front(subject, content, error)


class PermalinkHandler(Handler):

     def render_front(self, entry_id):
	entry=Blog.get_by_id(long(entry_id))
        self.render("permalink_blog.html", entry=entry)


     def get(self):
	uri_permalink=self.request.path_info
	result=uri_permalink.replace("/blog/","")
	self.render_front(result)


app = webapp2.WSGIApplication([('/blog', BlogHandler), ('/blog/newpost', NewPostHandler), (r'/blog/[0-9]+', PermalinkHandler)], debug=True)
