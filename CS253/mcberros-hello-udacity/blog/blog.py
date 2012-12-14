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
import json
import time
from datetime import datetime

from google.appengine.api import memcache
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
    uri=db.StringProperty()
    subject=db.StringProperty(required = True)
    content=db.TextProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)
    last_modified=db.DateTimeProperty(auto_now = True)

def top_posts(update=False):
    key_entries='top'
    key_time='time_cache'
    cache_time=memcache.get(key_time)
    entries=memcache.get(key_entries)
    if (entries == None) or (cache_time == None) or update:
        entries=db.GqlQuery("SELECT * FROM Blog ORDER BY last_modified DESC limit 10")
        entries=list(entries)
	cache_time=time.time()
        memcache.set(key_entries,entries)
	memcache.set(key_time,cache_time)
    return entries,cache_time

def permalink_post(uri_permalink,update=False):
    key_permalink=uri_permalink
    id_permalink=uri_permalink.replace("/blog/","")
    key_time='time_cache'+id_permalink
    cache_time=memcache.get(key_time)
    entry_permalink=memcache.get(key_permalink)
    if (entry_permalink == None) or (cache_time == None) or update:
	entry_permalink=Blog.get_by_id(long(id_permalink))
        cache_time=time.time()
        memcache.set(key_permalink,entry_permalink)
        memcache.set(key_time,cache_time)
    return entry_permalink,cache_time



class BlogHandler(Handler):
    def render_front(self):
	entries,cache_time=top_posts()
	now = time.time()
	difference = int(now - cache_time)
	self.render("front_blog.html", entries=entries,time=difference)

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
	   top_posts(True)
	   id_entry=c.key()
	   str_id_key=str(id_entry.id())
	   uri="/blog/"+str_id_key
	   c.uri=uri
	   c.put()
	   top_posts(True)
           permalink_post(uri,True)
           self.redirect(uri)
        else:
           error="we need both a subject and a content"
           self.render_front(subject, content, error)


class PermalinkHandler(Handler):

     def render_front(self, uri):
	entry,cache_time=permalink_post(uri)
        now = time.time()
        difference = int(now - cache_time)
        self.render("permalink_blog.html", entry=entry,time=difference)


     def get(self):
	uri_permalink=self.request.path_info
	self.render_front(uri_permalink)

class JsonHandler(webapp2.RequestHandler):

    def get(self):
	entries=db.GqlQuery("SELECT * FROM Blog ORDER BY last_modified DESC limit 10")
	self.response.headers['Content-Type']='application/json;charset=UTF-8' 	
	list_entries=[]
	date_format="%a %b %d %H:%M:%S %Y"
	for entry in entries:
	    list_entries.append(dict([('subject', entry.subject), ('content', entry.content), ('created', entry.created.strftime(date_format)),('last_modified',entry.last_modified.strftime(date_format))]))
	blog_json=json.dumps(list_entries)
	self.response.out.write(blog_json)

class PermalinkJsonHandler(webapp2.RequestHandler):

    def get(self):
	uri_permalink=self.request.path_info
        entry_id=uri_permalink.replace("/blog/","")
	entry_id=entry_id.replace(".json","")
	entry=Blog.get_by_id(long(entry_id))
        self.response.headers['Content-Type']='application/json;charset=UTF-8'
        date_format="%a %b %d %H:%M:%S %Y"
        dict_entry=dict([('subject', entry.subject), ('content', entry.content), ('created', entry.created.strftime(date_format)),('last_modified',entry.last_modified.strftime(date_format))])
        entry_json=json.dumps(dict_entry)
        self.response.out.write(entry_json)

class FlushHandler(webapp2.RequestHandler):
    def get(self):
	memcache.flush_all()	
	self.redirect('/blog')




app = webapp2.WSGIApplication([('/blog', BlogHandler), ('/blog/newpost', NewPostHandler), (r'/blog/[0-9]+', PermalinkHandler),('/blog/.json',JsonHandler),(r'/blog/[0-9]+'+'.json', PermalinkJsonHandler),('/blog/flush',FlushHandler)], debug=True)
