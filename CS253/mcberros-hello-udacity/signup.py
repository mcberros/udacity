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
import webapp2
import re
import os
import jinja2
import random
import string
import hashlib
import hmac
from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape =True)

SECRET = 'imsosecret'

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    value = h.split('|')[0]
    if h == make_secure_val(value):
        return value

class User(db.Model):
    username=db.StringProperty(required = True)
    password=db.StringProperty(required = True)

class Validator:
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PWD_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE=re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    MSG_ERR_USER="That's not a valid username."
    MSG_ERR_PWD="That wasn't a valid password."
    MSG_ERR_V_PWD="Your passwords didn't match."
    MSG_ERR_EMAIL="That's not a valid email."

    def valid_username(self,username=""):
        is_valid=True
    	if not self.USER_RE.match(username):
       	   is_valid=False
    	return is_valid

    def valid_password(self,password=""):
        is_valid=True
        if not self.PWD_RE.match(password):
           is_valid=False
        return is_valid

    def valid_match_pwd(self,password="",verify=""):
        is_valid=True
        if password!=verify:
           is_valid=False
        return is_valid


    def valid_email(self,email=""):
        is_valid=True
        if not self.EMAIL_RE.match(email):
           is_valid=False
        return is_valid


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(Self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class SignUpHandler(Handler):
	
	validator=Validator()

	def render_front(self, username="", password="", verify="", error_username="", error_password="", error_v_password="", email="", error_email=""):
            self.render("form_signup.html", username=username, password=password, verify=verify, error_username=error_username, error_password=error_password, error_v_password=error_v_password, email=email, error_email=error_email)

	def get(self):
	    self.render_front()

	def post(self):

	    in_username=self.request.get('username')
            in_password=self.request.get('password')
            in_verify=self.request.get('verify')
	    in_email=self.request.get('email')
	    err_msg={'error_username':"",'error_password':"",'error_v_password':"",'error_email':""}
	
	    is_valid_username=self.validator.valid_username(in_username)

	    if (not is_valid_username):
	    	err_msg['error_username']=self.validator.MSG_ERR_USER

	    is_valid_password=self.validator.valid_password(in_password)
	    is_valid_match_pwd=self.validator.valid_match_pwd(in_password,in_verify)

	    if (not is_valid_password):
		err_msg['error_password']=self.validator.MSG_ERR_PWD
	    else:
		if (not is_valid_match_pwd):
		   err_msg['error_v_password']=self.validator.MSG_ERR_V_PWD

	    is_valid_email=self.validator.valid_email(in_email)
	    if (not is_valid_email):
		err_msg['error_email']=self.validator.MSG_ERR_EMAIL

	    if err_msg['error_username']=="" and err_msg['error_password']=="" and err_msg['error_v_password']=="" and err_msg['error_email']=="":
		u=User(username=in_username,password=in_password)
                u.put()
		new_cookie_val = make_secure_val(str(in_username))
		self.response.headers.add_header('Set-Cookie','username=%s; Path=/' % new_cookie_val)
                self.redirect("/blog/welcome")
	    else:
		self.render_front(in_username,"","",err_msg['error_username'],err_msg['error_password'],err_msg['error_v_password'],in_email,err_msg['error_email'])



class WelcomeHandler(Handler):
	def get(self):
            username=self.request.cookies.get('username')
	    if username:
               cookie_val=check_secure_val(username)
               if cookie_val:
		  self.render("welcome.html",username=cookie_val)
	       else:
		  self.redirect("/blog/signup")


class UsersHandler(Handler):
	def render_front(self):
            users=db.GqlQuery("SELECT * FROM User")
            self.render("users.html", users=users)

        def get(self):
	    self.render_front()


app = webapp2.WSGIApplication([('/blog/signup',SignUpHandler),('/blog/welcome',WelcomeHandler),('/blog/users',UsersHandler)], debug=True)
