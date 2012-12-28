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
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

PAGE_RE = r'/?(?:[a-zA-Z0-9_-]+/?)*'
DOCUMENT_ROOT='/wiki'


class ViewHandler(render.Handler):

    def get(self):
	#Tenemos que comprobar si existe cookie con usuario
	# Si no existe cookie con usuario debemos redirigir a view_login.html
	# Si existe cookie de usuario debemos redirigir a view_user.html
	#En ambos casos hay que ver la URI para ver el post y dar una vista de su contenido
	# Por tanto, primero buscamos el contenido asociado a esa URI
	uri_post=self.request.path_info
	uri_history=DOCUMENT_ROOT+"/_history"+uri_post.replace(DOCUMENT_ROOT,"")

        param=self.request.get('v')
        if not param:
	   entry=db.GqlQuery("SELECT * FROM WikiPost WHERE uri=:1 ORDER BY created DESC limit 1",uri_post).get()
	else:
	   entry=wiki_post.WikiPost.get_by_id(int(param))

	cookie_val=self.request.cookies.get('valid')
        if not cookie_val:
	   self.render("view_login.html", uri_history=uri_history, entry=entry)
	else:
	   uri_edit=uri_history.replace("/_history","/_edit")
	   if entry:	
              username=hash_cookie.check_secure_val(cookie_val)
              self.render("view_user.html", uri_edit=uri_edit, uri_history=uri_history, username=username, entry=entry)
	   else:
	      self.redirect(uri_edit)
 


class HistoryHandler(render.Handler):

	def get(self):
   	    uri_post=self.request.path_info
	    uri_post=uri_post.replace("/_history","")
            entries=db.GqlQuery("SELECT * FROM WikiPost WHERE uri=:1 ORDER BY created DESC",uri_post)
	    cookie_val=self.request.cookies.get('valid')
	    if entries:
               if not cookie_val:
                  self.render("history_view.html",entries=entries)
               else:
		  uri_edit=DOCUMENT_ROOT+"/_edit"+uri_post.replace(DOCUMENT_ROOT,"")
                  username=hash_cookie.check_secure_val(cookie_val)
                  self.render("history_edit.html", uri_edit=uri_edit, uri_view=uri_post, username=username, entries=entries)


class EditHandler(render.Handler):

        def get(self):
	    uri_post=self.request.path_info
            uri_post=uri_post.replace("/_edit","")
	    param=self.request.get('v')
            if not param:
	       entry=db.GqlQuery("SELECT * FROM WikiPost WHERE uri=:1 ORDER BY created DESC limit 1",uri_post).get()
            else:
                entry=wiki_post.WikiPost.get_by_id(int(param))

	    cookie_val=self.request.cookies.get('valid')

 	    if not cookie_val:
		self.render("view_login.html",entry=entry)
	    else:
		username=hash_cookie.check_secure_val(cookie_val)
		if entry:
                    self.render("edit.html", uri=uri_post,username=username, content=entry.content)
		else:
		    self.render("edit.html", uri=uri_post,username=username, content="") 


	def post(self):
	    uri_edit=self.request.path_info
	    uri_post=uri_edit.replace("/_edit","")
	    content=self.request.get("content")
	    entry=wiki_post.WikiPost(uri=uri_post, content=content)
            entry.put()
            entry.id=entry.key().id()
	    entry.uri_history_view=uri_post+"?v="+str(entry.key().id())
	    entry.uri_history_edit=uri_edit+"?v="+str(entry.key().id())
            entry.put()

	    cookie_val=self.request.cookies.get('valid')
            if cookie_val:
                username=hash_cookie.check_secure_val(cookie_val)
                self.redirect(uri_post)


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
		self.redirect(DOCUMENT_ROOT)
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




app = webapp2.WSGIApplication([(DOCUMENT_ROOT+'/signup',SignUpHandler),(DOCUMENT_ROOT+'/login',LoginHandler),(DOCUMENT_ROOT+'/logout',LogoutHandler),(DOCUMENT_ROOT+'/_edit' + PAGE_RE, EditHandler),(DOCUMENT_ROOT+'/_history'+PAGE_RE,HistoryHandler),(DOCUMENT_ROOT+PAGE_RE, ViewHandler)], debug=True)

