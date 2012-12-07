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

import render
import validator
import user
import salt
import hash_cookie
from google.appengine.ext import db


#Clases del flujo de navegacion

class SignUpHandler(render.Handler):
	
	validator=validator.Validator()

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
	    else:
		exist_user=self.validator.exist_username(in_username)
		if exist_user:
		   err_msg['error_username']=self.validator.MSG_EXIST_USER

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
		password_hash=salt.make_pw_hash(in_username, in_password)
		u=user.User(username=in_username, password=password_hash.split(",")[0], salt=password_hash.split(",")[1])
                u.put()
		new_cookie_val = hash_cookie.make_secure_val(str(in_username))
		self.response.headers.add_header('Set-Cookie','user_id=%s; Path=/' % new_cookie_val)
                self.redirect("/blog/welcome")
	    else:
		self.render_front(in_username,"","",err_msg['error_username'],err_msg['error_password'],err_msg['error_v_password'],in_email,err_msg['error_email'])


class WelcomeHandler(render.Handler):
	def get(self):
            username=self.request.cookies.get('user_id')
	    if username:
               cookie_val=hash_cookie.check_secure_val(username)
               if cookie_val:
		  self.render("welcome.html",username=cookie_val)
	       else:
		  self.redirect("/blog/signup")


class UsersHandler(render.Handler):
	def render_front(self):
            users=db.GqlQuery("SELECT * FROM User")
            self.render("users.html", users=users)

        def get(self):
	    self.render_front()


app = webapp2.WSGIApplication([('/blog/signup',SignUpHandler),('/blog/welcome',WelcomeHandler),('/blog/users',UsersHandler)], debug=True)
