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

import wiki_post
import user

import render
import validator
import salt
import hash_cookie

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape =True)

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
DOCUMENT_ROOT='/wiki'


class ViewHandler(render.Handler):
    def render_front(self):
        entry=wiki_post.get_post()
        self.render("view_login.html", entry=entry)

    def get(self):
	self.render_front()


class SignUpHandler(render.Handler):

        validator=validator.Validator()

        def set_secure_cookie(self,name, val):
            cookie_val = hash_cookie.make_secure_val(val)
            self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % (name, cookie_val))

        def render_front(self, username="", password="", verify="", error_username="", error_password="", error_verify="", email="", error_email=""):
            self.render("form_signup.html", username=username, password=password, verify=verify, error_username=error_username, error_password=error_password, error_verify=error_verify, email=email, error_email=error_email)

        def get(self):
            self.render_front()

        def post(self):
            in_username=self.request.get('username')
            in_password=self.request.get('password')
            in_verify=self.request.get('verify')
            in_email=self.request.get('email')
            err_msg={'error_username':"",'error_password':"",'error_verify':"",'error_email':""}

            is_valid_username=self.validator.valid_username(in_username)

            if (not is_valid_username):
                err_msg['error_username']=self.validator.MSG_ERR_USER
            else:
                exist_user=self.validator.exist_username(in_username)
                if exist_user:
                   err_msg['error_username']=self.validator.MSG_EXIST_USER

            is_valid_password=self.validator.valid_sign_password(in_password)
            is_valid_match_pwd=self.validator.valid_match_pwd(in_password,in_verify)

            if (not is_valid_password):
                err_msg['error_password']=self.validator.MSG_ERR_PWD
            else:
                if (not is_valid_match_pwd):
                   err_msg['error_verify']=self.validator.MSG_ERR_V_PWD

            is_valid_email=self.validator.valid_email(in_email)
            if (not is_valid_email):
                err_msg['error_email']=self.validator.MSG_ERR_EMAIL

            if err_msg['error_username']=="" and err_msg['error_password']=="" and err_msg['error_verify']=="" and err_msg['error_email']=="":
                password_hash=salt.make_pw_hash(in_username, in_password)
                u=user.User(username=in_username, password=password_hash.split(",")[0], salt=password_hash.split(",")[1])
                u.put()
                self.set_secure_cookie('valid',str(in_username))
                self.redirect("/blog/welcome")
            else:
		self.render_front(in_username,"","",err_msg['error_username'],err_msg['error_password'],err_msg['error_verify'],in_email,err_msg['error_email'])

class LoginHandler(render.Handler):

        validator=validator.Validator()

        def set_secure_cookie(self,name, val):
            cookie_val = hash_cookie.make_secure_val(val)
            self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % (name, cookie_val))

        def render_front(self, username="", password="", error_login=""):
            self.render("form_login.html", username=username, password=password, error_login=error_login)

        def get(self):
            self.render_front()

        def post(self):
            in_username=self.request.get('username')
            in_password=self.request.get('password')
            error_login="Invalid login"

            if self.validator.exist_username(in_username) and self.validator.valid_bbdd_password(in_username,in_password):
                self.set_secure_cookie('valid',str(in_username))
                self.redirect(DOCUMENT_ROOT)
            else:
                self.render_front(in_username,"",error_login)

class LogoutHandler(render.Handler):

        def empty_cookie(self,name):
            self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % (name, ""))

        def get(self):
            self.empty_cookie('valid')
            self.redirect(DOCUMENT_ROOT)


class EditHandler(render.Handler):
	def render_front(self):
            self.render("edit.html",entry="mcberros")

        def get(self):
            self.render_front()




app = webapp2.WSGIApplication([(DOCUMENT_ROOT, ViewHandler),(DOCUMENT_ROOT+'/_edit',EditHandler),(DOCUMENT_ROOT+'/signup',SignUpHandler),(DOCUMENT_ROOT+'/login',LoginHandler),(DOCUMENT_ROOT+'/logout',LogoutHandler)], debug=True)

