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

form_problem2_2="""
<form method="post">
	<b>Signup</b>
	<br><br>
	<label>Username <input type="text" name="username" value="%(username)s"> </label><span style="color: red"> %(error_username)s</span></label>
	<br>
	<label>Password <input type="password" name="password" value="%(password)s"></label><span style="color: red"> %(error_password)s</span></label>
	<br>
	<label>Verify Password <input type="password" name="verify" value="%(verify)s"></label><span style="color: red"> %(error_v_password)s</span></label>
	<br>
	<label>Email(optional) <input type="text" name="email" value="%(email)s"> <span style="color: red"> %(error_email)s</span></label>
	<br>
	<input type="submit">
</form>
"""

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username=""):
    is_valid=True
    if not USER_RE.match(username):
       is_valid=False
    return is_valid

def escape_html(s):
    escape_list=(("&","&amp;"),(">","&gt;"),("<","&lt;"),('"',"&quot;"))
    for (i,o) in escape_list:
        s=s.replace(i,o)
    return s

class Problem2_2Handler(webapp2.RequestHandler):
	PWD_RE = re.compile(r"^.{3,20}$")
	EMAIL_RE=re.compile(r"^[\S]+@[\S]+\.[\S]+$")
	MSG_ERR_USER="That's not a valid username."
	MSG_ERR_PWD="That wasn't a valid password."
	MSG_ERR_V_PWD="Your passwords didn't match."
	MSG_ERR_EMAIL="That's not a valid email."

	    
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

	def write_form_problem2_2(self, username="", password="", verify="", error_username="", error_password="", error_v_password="", email="", error_email=""):
	    self.response.write(form_problem2_2 % {'username':escape_html(username), 'password':"",'verify':"",'error_username':error_username, 'error_password':error_password, 'error_v_password':error_v_password, 'email':escape_html(email), 'error_email':error_email})

	def get(self):
	    self.write_form_problem2_2()

	def post(self):
	    in_username=self.request.get('username')
            in_password=self.request.get('password')
            in_verify=self.request.get('verify')
	    in_email=self.request.get('email')
	    err_msg={'error_username':"",'error_password':"",'error_v_password':"",'error_email':""}
	
	    is_valid_username=valid_username(in_username)

	    if (not is_valid_username):
	    	err_msg['error_username']=self.MSG_ERR_USER

	    is_valid_password=self.valid_password(in_password)
	    is_valid_match_pwd=self.valid_match_pwd(in_password,in_verify)

	    if (not is_valid_password):
		err_msg['error_password']=self.MSG_ERR_PWD
	    else:
		if (not is_valid_match_pwd):
		   err_msg['error_v_password']=self.MSG_ERR_V_PWD

	    is_valid_email=self.valid_email(in_email)
	    if (not is_valid_email):
		err_msg['error_email']=self.MSG_ERR_EMAIL

	    if err_msg['error_username']=="" and err_msg['error_password']=="" and err_msg['error_v_password']=="" and err_msg['error_email']=="":
                self.redirect("/problem2_2/welcome?username=" + in_username)
	    else:
		self.write_form_problem2_2(in_username,"","",err_msg['error_username'],err_msg['error_password'],err_msg['error_v_password'],in_email,err_msg['error_email'])

		


class Welcome_P2_2Handler(webapp2.RequestHandler):
	def get(self):
	    username=self.request.get('username')
	    if valid_username(username):
	   	self.response.out.write("Welcome, " + username + "!")
	    else:
		self.redirect("/problem2_2/signup")

app = webapp2.WSGIApplication([('/problem2_2/signup',Problem2_2Handler),('/problem2_2/welcome',Welcome_P2_2Handler)], debug=True)
